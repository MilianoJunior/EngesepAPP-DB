import asynckivy as ak

async def some_task(button):
    # wait for 1sec
    dt = await ak.sleep(3)
    print(f'{dt} seconds have passed')
    
    # wait until a button is pressed
    # await ak.event(button, 'on_press')

    # wait until 'button.x' changes
    # __, x = await ak.event(button, 'x')
    # print(f'button.x is now {x}')

    # wait until 'button.x' becomes greater than 100
    # if button.x <= 100:
    #     __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
    #     print(f'button.x is now {x}')

    # wait until EITHER a button is pressed OR 5sec passes
    # tasks = await ak.or_(
    #     ak.event(button, 'on_press'),
    #     ak.sleep(5),
    # )
    # print("The button was pressed" if tasks[0].done else "5sec passed")

    # # wait until BOTH a button is pressed AND 5sec passes"
    # tasks = await ak.and_(
    #     ak.event(button, 'on_press'),
    #     ak.sleep(5),
    # )

ak.start(some_task('some_button'))