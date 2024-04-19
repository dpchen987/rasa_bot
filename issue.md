<!-- 问题记录 -->

  # - rule: check express status
  #   steps:
  #     - or:
  #       - intent: check_express_status
  #       - intent: has_sent_or_not
  #       - intent: pretend_sent
  #       - intent: if_has_lost
  #     - action: action_form_count_rollback
  #     - action: collect_express_id_form
  #     - active_loop: collect_express_id_form

#  激活form的逻辑放在rules里可以实现，但是放在story里实现不了，执行完action_form_count_rollback后就会出现fallback.
# 即使把其他所有story和rules删了也一样。


# 运单号识别优化
静安区裕园路309号
韵达尾号6420


# slot_name优化
'呃，我姓呃我姓赵 
'slot_name': '呃先生'
'slot_name': '有'
郭店郭店街道826地质局宿舍。
'slot_name': '郭 郭'
'slot_name': '杨鑫路 杨先生'