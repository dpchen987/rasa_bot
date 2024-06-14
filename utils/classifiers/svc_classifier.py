import logging
from typing import Any, Text, Dict, List, Type, Tuple

import joblib
from scipy.sparse import hstack, vstack, csr_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.nlu.classifiers import LABEL_RANKING_LENGTH
from rasa.nlu.featurizers.featurizer import Featurizer
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import TEXT, INTENT
from rasa.utils.tensorflow.constants import RANKING_LENGTH
from typing import Any, Dict, List, Optional, Text, Tuple, Type
logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER, is_trainable=True
)
class SVCClassifier(IntentClassifier, GraphComponent):
    """Intent classifier using the LinearSVC."""

    @classmethod
    def required_components(cls) -> List[Type]:
        """Components that should be included in the pipeline before this component."""
        return [Featurizer]

    @staticmethod
    def required_packages() -> List[Text]:
        """Any extra python dependencies required for this component to run."""
        return ["sklearn"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config (see parent class for full docstring)."""
        return {
            # C parameter of the svm - cross validation will select the best value
            "C": [1, 2, 5, 10, 20, 100],
            # gamma parameter of the svm
            "gamma": [0.1],
            # the kernels to use for the svm training - cross validation will
            # decide which one of them performs best
            "kernels": ["linear"],
            # We try to find a good number of cross folds to use during
            # intent training, this specifies the max number of folds
            "max_cross_validation_folds": 5,
            # Scoring function used for evaluating the hyper parameters
            # This can be a name or a function (cfr GridSearchCV doc for more info)
            "scoring_function": "f1_weighted",
            "num_threads": 1,
        }

    def __init__(
        self,
        config: Dict[Text, Any],
        name: Text,
        model_storage: ModelStorage,
        resource: Resource,
        clf: Optional["sklearn.model_selection.GridSearchCV"] = None,
    ) -> None:
        """Construct a new classifier."""
        self.name = name
        self.component_config = config

        # We need to use these later when saving the trained component.
        self._model_storage = model_storage
        self._resource = resource
        self.clf = clf
        
    def _create_classifier(
        self, num_threads: int
    ) -> "sklearn.model_selection.GridSearchCV":
        C = self.component_config["C"]
        kernels = self.component_config["kernels"]
        gamma = self.component_config["gamma"]
        # dirty str fix because sklearn is expecting
        # str not instance of basestr...
        tuned_parameters = [
            {"C": C, "gamma": gamma, "kernel": [str(k) for k in kernels]}
        ]

        # aim for 5 examples in each fold

        return GridSearchCV(
            SVC(C=1, probability=True, class_weight="balanced"),
            param_grid=tuned_parameters,
            n_jobs=num_threads,
            cv=self.component_config["max_cross_validation_folds"],
            scoring=self.component_config["scoring_function"],
            verbose=1,
        )
    def _create_X(self, messages: List[Message]) -> csr_matrix:
        """This method creates a sparse X array that can be used for predicting."""
        X = []
        for e in messages:
            # First element is sequence features, second is sentence features
            sparse_feats = e.get_sparse_features(attribute=TEXT)[1]
            # First element is sequence features, second is sentence features
            dense_feats = e.get_dense_features(attribute=TEXT)[1]
            together = hstack(
                [
                    csr_matrix(sparse_feats.features if sparse_feats else []),
                    csr_matrix(dense_feats.features if dense_feats else []),
                ]
            )
            X.append(together)
        return vstack(X)

    def _create_training_matrix(
        self, training_data: TrainingData
    ) -> Tuple[csr_matrix, List[str]]:
        """This method creates a scikit-learn compatible (X, y) training pairs."""
        y = []

        examples = [
            e
            for e in training_data.intent_examples
            if (e.get("intent") and e.get("text"))
        ]

        for e in examples:
            y.append(e.get(INTENT))

        return self._create_X(examples), y

    def train(self, training_data: TrainingData) -> Resource:
        """Train the intent classifier on a data set."""
        X, y = self._create_training_matrix(training_data)
        if X.shape[0] == 0:
            logger.debug(
                f"Cannot train '{self.__class__.__name__}'. No data was provided. "
                f"Skipping training of the classifier."
            )
            return self._resource
        num_threads = self.component_config["num_threads"]
        self.clf = self._create_classifier(num_threads)
        self.clf.fit(X, y)
        self.persist()

        return self._resource

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "SVCClassifier":
        """Creates a new untrained component (see parent class for full docstring)."""
        return cls(config, execution_context.node_name, model_storage, resource)

    def process(self, messages: List[Message]) -> List[Message]:
        """Return the most likely intent and its probability for a message."""
        X = self._create_X(messages)
        probas = self.clf.predict_proba(X)
        for idx, message in enumerate(messages):
            intents = self.clf.classes_
            intent_ranking = [
                {"name": k, "confidence": v} for k, v in zip(intents, probas[idx])
            ]
            sorted_ranking = sorted(intent_ranking, key=lambda e: -e["confidence"])
            intent = sorted_ranking[0]
            if self.config[RANKING_LENGTH] > 0:
                sorted_ranking = sorted_ranking[: self.config[RANKING_LENGTH]]
            message.set("intent", intent, add_to_output=True)
            message.set("intent_ranking", sorted_ranking, add_to_output=True)
        return messages


    def persist(self) -> None:
        """Persist this model into the passed directory."""
        with self._model_storage.write_to(self._resource) as model_dir:
            path = model_dir / f"{self._resource.name}.joblib"
            joblib.dump(self.clf, path)
            logger.debug(f"Saved intent classifier to '{path}'.")

    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> "SVCClassifier":
        """Loads trained component (see parent class for full docstring)."""
        try:
            with model_storage.read_from(resource) as model_dir:
                classifier = joblib.load(model_dir / f"{resource.name}.joblib")
                component = cls(
                    config, execution_context.node_name, model_storage, resource
                )
                component.clf = classifier
                return component
        except ValueError:
            logger.debug(
                f"Failed to load {cls.__class__.__name__} from model storage. Resource "
                f"'{resource.name}' doesn't exist."
            )
            return cls.create(config, model_storage, resource, execution_context)

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Process the training data."""
        self.process(training_data.training_examples)
        return training_data

    @classmethod
    def validate_config(cls, config: Dict[Text, Any]) -> None:
        """Validates that the component is configured properly."""
        pass
