from linebot.models import (ButtonsTemplate, DatetimePickerAction,
                            MessageEvent, PostbackAction, PostbackEvent,
                            TemplateSendMessage, TextMessage)

ATTEND_TEMPLATE = TemplateSendMessage(
        alt_text='勤務を開始します！',
        template=ButtonsTemplate(
            title='出勤',
            text='選択してください！',
            actions=[
                PostbackAction(
                    label='出勤',
                    display_text='出勤',
                    data='action=attend&manual=false'
                ),
                PostbackAction(
                    label='出勤（手入力）',
                    display_text='出勤（手入力）',
                    data='action=attend&manual=true'
                )
            ]
        )
    )

LOCATION_TEMPLATE = TemplateSendMessage(
        alt_text='勤務場所を登録します！',
        template=ButtonsTemplate(
            title='勤務場所登録',
            text='選択してください！',
            actions=[
                PostbackAction(
                    label='出社',
                    display_text='出社',
                    data='action=locate&location=office'
                ),
                PostbackAction(
                    label='在宅勤務',
                    display_text='在宅勤務',
                    data='action=locate&location=fullremote'
                ),
                PostbackAction(
                    label='在宅勤務4h未満',
                    display_text='在宅勤務4h未満',
                    data='action=locate&location=remotelt4h'
                )
            ]
        )
    )

ATTEND_TIME_ACTION = DatetimePickerAction(
    label='時刻を選択',
    data='action=time&type=attend',
    mode='time',
    initial='10:00'
)
