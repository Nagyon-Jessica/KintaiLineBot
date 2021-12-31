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
                    data='action=locate&location=1'
                )
            ),
            QuickReplyButton(
                action=PostbackAction(
                    label='在宅勤務',
                    display_text='在宅勤務',
                    data='action=locate&location=2'
                )
            ),
            QuickReplyButton(
                action=PostbackAction(
                    label='在宅勤務4h未満',
                    display_text='在宅勤務4h未満',
                    data='action=locate&location=3'
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

CHECKOUT_TIME_TEMPLATE = QuickReply(
    items=[
        QuickReplyButton(
            action=DatetimePickerAction(
                label='時刻を選択',
                data='action=time&type=checkout',
                mode='time',
                initial='18:30'
            )
        )
    ]
)

CHECKOUT_TEMPLATE = TextSendMessage(
    text='打刻が完了しました！\n退勤時は下のボタンを選択してください！',
    quick_reply=QuickReply(
        items=[
            QuickReplyButton(
                action=PostbackAction(
                    label='退勤',
                    display_text='退勤',
                    data='action=checkout&manual=false'
                )
            ),
            QuickReplyButton(
                action=PostbackAction(
                    label='退勤（手入力）',
                    display_text='退勤（手入力）',
                    data='action=checkout&manual=true'
                )
            ),
        ]
    )
)

NOTE_TEMPLATE = TextSendMessage(
    text='備考を入力しますか？',
    quick_reply=QuickReply(
        items=[
            QuickReplyButton(
                action=PostbackAction(
                    label='はい',
                    display_text='はい',
                    data='action=note&reply=yes'
                )
            ),
            QuickReplyButton(
                action=PostbackAction(
                    label='いいえ',
                    display_text='いいえ',
                    data='action=note&reply=no'
                )
            ),
        ]
    )
)
