import requests
import random
import time
data_ls = [
{'sender': 1710980964.10119, 'message': 'servicer：你好，很高兴为您服务，请问有什么可以帮您'},
{'sender': 1710980964.10119, 'message': '嗯，我想问一下，我这边呢有一个件了，然后是到集运仓中转中通快递的。然后他那边理赔说理赔到你们这个圆通，我们第一单物流是圆通发出的嘛'},
{'sender': 1710980964.10119, 'message': 'servicer：，你现在这个东'},
{'sender': 1710980964.10119, 'message': '，他那我我问一下这个怎么你们那边有收到吗？那个圆通的那个'},
{'sender': 1710980964.10119, 'message': '就中通的理赔件了'},
{'sender': 1710980964.10119, 'message': 'servicer：，您说的是哪个单号呢？女士，请您提供一下圆通的单号呢？女士'},
{'sender': 1710980964.10119, 'message': '啊'},
{'sender': 1710980964.10119, 'message': '，好，yt8953 '},
{'sender': 1710980964.10119, 'message': 'servicer：8953 ，然后呢'},
{'sender': 1710980964.10119, 'message': '5158'},
{'sender': 1710980964.10119, 'message': '59768'},
{'sender': 1710980964.10119, 'message': 'servicer：浙江台州寄出，寄往陕西省西安市，是吗'},
{'sender': 1710980964.10119, 'message': '嗯，对'},
{'sender': 1710980964.10119, 'message': 'servicer：？这是一月份的件是吗'},
{'sender': 1710980964.10119, 'message': '对'},
{'sender': 1710980964.10119, 'message': '，这个是'},
{'sender': 1710980964.10119, 'message': '01月28日的件，然后是02月05日，你们到中转仓的'},
{'sender': 1710980964.10119, 'message': '，然后中转仓，再从转寄的话是中通快递，然后那边丢件了，他说理赔到你们圆通公司的'},
{'sender': 1710980964.10119, 'message': 'servicer：，请问您贵姓是怎么称呼您女士？您是发件人吗？还是后来的'},
{'sender': 1710980964.10119, 'message': '啊，我姓刘'},
{'sender': 1710980964.10119, 'message': '啊'},
{'sender': 1710980964.10119, 'message': 'servicer：您是发件人吗？还是收货人呢'},
{'sender': 1710980964.10119, 'message': '，我是发起人'},
{'sender': 1710980964.10119, 'message': 'servicer：？这是邮寄的什么物品呢？女士方便提供一下吗'},
{'sender': 1710980964.10119, 'message': '嗯，垃圾桶'},
{'sender': 1710980964.10119, 'message': 'servicer：？垃圾桶是吗'},
{'sender': 1710980964.10119, 'message': '。对'},
{'sender': 1710980964.10119, 'message': 'servicer：？多少钱呢？大家真女士'},
{'sender': 1710980964.10119, 'message': '嗯，81 '},
{'sender': 1710980964.10119, 'message': 'servicer：就这个件的话，是到了中转仓，中转仓那边拒收退回的吗'},
{'sender': 1710980964.10119, 'message': '不是拒收退回的，是他重新转发到新疆的吗？这个不是'},
{'sender': 1710980964.10119, 'message': '，然后在路途中转新疆的路途中丢件了'},
{'sender': 1710980964.10119, 'message': 'servicer：，那就是没有传寄到新疆，是吗'},
{'sender': 1710980964.10119, 'message': '。对，不是转寄到新疆了，已经到新疆了，然后转再发往收货人地那个路中丢失的'},
{'sender': 1710980964.10119, 'message': 'servicer：？要的物流'},
{'sender': 1710980964.10119, 'message': 'servicer：，那您这个件我们稍后跟王里去核实之后，给您回电处理一下。因为他这边第一段物流显示是已经签收了，您说是呃，第2个物流'},
{'sender': 1710980964.10119, 'message': '就到乌鲁木齐嘛。那边还在乌鲁木齐的时候，嗯，乌鲁木齐转运中心已经丢件了'},
{'sender': 1710980964.10119, 'message': '。嗯，好的'},
{'sender': 1710980964.10119, 'message': '，对，他们是他们那边说理赔'},
{'sender': 1710980964.10119, 'message': 'servicer：，但是我这边没有查询到网点，这边是上报理赔的情况'},
{'sender': 1710980964.10119, 'message': '，理赔到你们公司的'},
{'sender': 1710980964.10119, 'message': '这样的了哦，好，那你帮我问一下吧'},
{'sender': 1710980964.10119, 'message': 'servicer：。对我们这边更往哪些去核实一下，对'},
{'sender': 1710980964.10119, 'message': '啊，好嗯，再见'},
{'sender': 1710980964.10119, 'message': 'servicer：您方便留下手机号码吗？女士'},
{'sender': 1710980964.10119, 'message': 'servicer：198 ，然后呢'},
{'sender': 1710980964.10119, 'message': '，198 '},
{'sender': 1710980964.10119, 'message': '576'},
{'sender': 1710980964.10119, 'message': 'servicer：，然后呢'},
{'sender': 1710980964.10119, 'message': '52536'},
{'sender': 1710980964.10119, 'message': 'servicer：，19857652536 ，对吗'},
{'sender': 1710980964.10119, 'message': '哦'},
{'sender': 1710980964.10119, 'message': 'servicer：？好的，我记下了，这边跟我联系，去核实一下之后给您回电处理一下。请问还有其他问题咨询吗'},
{'sender': 1710980964.10119, 'message': '，哎呀'},
{'sender': 1710980964.10119, 'message': '啊没有了'},
{'sender': 1710982409.10119, 'message': '啊，我在你们圆通好几个快递都给我算成放到快递柜儿了。然后我不允许放快递柜，就要上门送到送上门'},
{'sender': 1710982409.10119, 'message': 'servicer：电话是零，福成沈梦玲，你好'},
{'sender': 1710982409.10119, 'message': 'servicer：啊，女士，您把那个快递单号告诉我'},
{'sender': 1710982409.10119, 'message': '快好几个快递呢。我我我我都要告诉你们，好几个快递都给我放空着'},
{'sender': 1710982409.10119, 'message': 'servicer：，您说'},
{'sender': 1710982409.10119, 'message': 'servicer：您先提供提供一下其中一个'},
{'sender': 1710982409.10119, 'message': '呃，9053 尾号你要填要'},
{'sender': 1710982409.10119, 'message': 'servicer：啊，说说一下完整的吧'},
{'sender': 1710982409.10119, 'message': 'servicer：，您说'},
{'sender': 1710982409.10119, 'message': '嗯yt'},
{'sender': 1710982409.10119, 'message': '1850'},
{'sender': 1710982409.10119, 'message': '8507'},
{'sender': 1710982409.10119, 'message': 'servicer：您说'},
{'sender': 1710982409.10119, 'message': '29053'},
{'sender': 1710982409.10119, 'message': 'servicer：好，您稍等啊'},
{'sender': 1710982409.10119, 'message': '。对我以后我我不允许他'},
{'sender': 1710982409.10119, 'message': 'servicer：，就您的好几个包裹都是被相同的放在这个蜂巢柜里面了，是吗'},
{'sender': 1710982409.10119, 'message': 'servicer：？嗯，您大概几个'},
{'sender': 1710982409.10119, 'message': 'servicer：您数一下女士'},
{'sender': 1710982409.10119, 'message': 'servicer：啊，那我们这边3个包裹好的，那您那您您报给我的单号一共3个，还是说是连单号一共4个'},
{'sender': 1710982409.10119, 'message': '一个两个'},
{'sender': 1710982409.10119, 'message': '两个'},
{'sender': 1710982409.10119, 'message': '，3个目前是目前显示是3个'},
{'sender': 1710982409.10119, 'message': '报名单号'},
{'sender': 1710982409.10119, 'message': '。呃，连单号应该是3个，然后你能不能能不能给我给我备注一下，以后不让放快递柜。因为我我我放快递柜很不方便。我每天开车从大门进来，你就直接我家里要没有人我我所有的快递，我所有的快递原来全部都是给我放家门口的。我丢件儿已也没有丢过件，从来没丢过件就已经丢丢年了。所以说就给我放家门口就可以了'},
{'sender': 1710982409.10119, 'message': 'servicer：？好的'},
{'sender': 1710982409.10119, 'message': 'servicer：啊，是给你添麻烦了'},
{'sender': 1710982409.10119, 'message': 'servicer：。好的，那您这边是收货人是收收货了，李女士是吧'},
{'sender': 1710982409.10119, 'message': '，我要不在的情况下'},
{'sender': 1710982409.10119, 'message': '过'},
{'sender': 1710982409.10119, 'message': 'servicer：？好，那我们这边的话让工作人员对接这个网点重新处理一下派送，然后给您回复'},
{'sender': 1710982409.10119, 'message': '好的，谢谢啊'},
{'sender': 1710982409.10119, 'message': 'servicer：。好的，不客气，女士，那您还有其他问题吗'},
{'sender': 1710982409.10119, 'message': '，没有了再见'},
{'sender': 1710982444.10119, 'message': 'servicer：您好，很高兴为您服务，请问有什么可以帮您'},
{'sender': 1710982444.10119, 'message': '对吧'},
{'sender': 1710982444.10119, 'message': 'servicer：？你好，女士'},
{'sender': 1710982444.10119, 'message': '？喂，你好，能不能帮我们把快递揽收一下'},
{'sender': 1710982444.10119, 'message': 'servicer：，请问您贵姓怎么称呼您女士'},
{'sender': 1710982444.10119, 'message': '弄王'},
{'sender': 1710982444.10119, 'message': 'servicer：，您是要寄件吗？还是插件呢'},
{'sender': 1710982444.10119, 'message': '用我啊'},
{'sender': 1710982444.10119, 'message': 'servicer：？好的女士，您是下单了吗'},
{'sender': 1710982444.10119, 'message': '。嗯是的'},
{'sender': 1710982444.10119, 'message': 'servicer：？是您这个来电的手机号码下的订单吗'},
{'sender': 1710982444.10119, 'message': '，不是不是'},
{'sender': 1710982444.10119, 'message': 'servicer：？那是哪个号码下的订单呢？麻烦您提供一下手机号码呢，女士'},
{'sender': 1710982444.10119, 'message': '18979'},
{'sender': 1710982444.10119, 'message': 'servicer：8000'},
{'sender': 1710982444.10119, 'message': '，不用不用不用'},
{'sender': 1710982444.10119, 'message': '570'},
{'sender': 1710982444.10119, 'message': 'servicer：890570 ，然后呢'},
{'sender': 1710982444.10119, 'message': '，你上面是有什么吗'},
{'sender': 1710982444.10119, 'message': 'servicer：，好的'},
{'sender': 1710982444.10119, 'message': '？稍等一下哈，我看一下'},
{'sender': 1710982444.10119, 'message': '那个189 '},
{'sender': 1710982444.10119, 'message': 'servicer：好的'},
{'sender': 1710982444.10119, 'message': '9347'},
{'sender': 1710982444.10119, 'message': 'servicer：，189 '},
{'sender': 1710982444.10119, 'message': '570'},
{'sender': 1710982444.10119, 'message': 'servicer：93470570 是吧'},
{'sender': 1710982444.10119, 'message': 'servicer：，18993470570 '},
{'sender': 1710982444.10119, 'message': 'servicer：，是这个号码下的订单吗'},
{'sender': 1710982444.10119, 'message': '是的'},
{'sender': 1710982444.10119, 'message': 'servicer：？您在平台上下的订单吗'},
{'sender': 1710982444.10119, 'message': '是的'},
{'sender': 1710982444.10119, 'message': 'servicer：？但是没有查询到订单号女士'},
{'sender': 1710982444.10119, 'message': '，我我们是怎么样'},
{'sender': 1710982444.10119, 'message': 'servicer：，好的，您再看一下呢'},
{'sender': 1710982444.10119, 'message': '？稍等一下，我再看一下哈'},
{'sender': 1710982444.10119, 'message': '啊，我报一下订单号，你你查一下吧'},
{'sender': 1710982444.10119, 'message': 'servicer：，请说女士'},
{'sender': 1710982444.10119, 'message': '，yt'},
{'sender': 1710982444.10119, 'message': '7452'},
{'sender': 1710982444.10119, 'message': 'servicer：，然后呢'},
{'sender': 1710982444.10119, 'message': '7702'},
]

ip_ls = ['10.130.118.125']
# ip_ls = ['10.197.235.10', '10.197.235.5', '10.197.235.6', '10.197.235.7']

while True:
    try:
        api_ip = random.choice(ip_ls)
        data = random.choice(data_ls)
        data['sender'] = 'a' + str(int(time.time())//40)
        url = f'http://{api_ip}:5006/webhooks/callassist/webhook'
        start_time = time.time()
        res = requests.post(url, json=data, timeout=3)
        d = res.json()
        # lst_msg = d[-1]['last_message']
        lst_msg = ''
        print(data['sender'], time.time() - start_time, api_ip)
    except Exception as e:
        print(api_ip, ':', e)