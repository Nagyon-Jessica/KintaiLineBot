from linebot.models import (DatetimePickerAction, PostbackAction, QuickReply,
                            QuickReplyButton, TextSendMessage)

ATTEND_TEMPLATE = TextSendMessage(
        text='勤務を開始します！選択してください！',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=PostbackAction(
                        label='出勤',
                        display_text='出勤',
                        data='action=attend&manual=false'
                    )
                ),
                QuickReplyButton(
                    action=PostbackAction(
                        label='出勤（手入力）',
                        display_text='出勤（手入力）',
                        data='action=attend&manual=true'
                    )
                ),
            ]
        )
    )

LOCATION_TEMPLATE = TextSendMessage(
        text='勤務場所を登録します！選択してください！',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=PostbackAction(
                        label='出社',
                        display_text='出社',
                        data='action=locate&location=office'
                    )
                ),
                QuickReplyButton(
                    action=PostbackAction(
                        label='在宅勤務',
                        display_text='在宅勤務',
                        data='action=locate&location=fullremote'
                    )
                ),
                QuickReplyButton(
                    action=PostbackAction(
                        label='在宅勤務4h未満',
                        display_text='在宅勤務4h未満',
                        data='action=locate&location=remotelt4h'
                    )
                )
            ]
        )
    )

ATTEND_TIME_TEMPLATE = QuickReply(
        items=[
            QuickReplyButton(
                action=DatetimePickerAction(
                    label='時刻を選択',
                    data='action=time&type=attend',
                    mode='time',
                    initial='10:00'
                )
            )
        ]
    )
