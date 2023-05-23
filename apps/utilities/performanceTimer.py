import time

def initiateTimer():
    return {
        '1.START:': 0,
        'Counter': 1,
        'Last_event': '1.START:',
        'Last_timeStamp': time.perf_counter(),
        'Total Time': 0
    }

def timePerformance(eventName:str, timer):
    new_timeStamp = time.perf_counter()
    last_counter = timer['Counter']
    new_counter = last_counter + 1
    new_event_key = str(new_counter)+'.'+eventName+':'
    timer[new_event_key] = new_timeStamp - timer['Last_timeStamp']
    timer['Last_event'] = new_event_key
    timer['Counter'] +=1
    timer['Last_timeStamp'] = new_timeStamp
    timer['Total Time']+=timer[new_event_key]
    return timer