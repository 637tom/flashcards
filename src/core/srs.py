def update_card_state(ease, interval, repetitions, grade):
    if not isinstance(ease, (int, float)):
        raise TypeError(f"Ease must be a number, got {type(ease).__name__}")
    ease = max(1.3, min(ease, 3.0))
    if grade < 3 :
        new_repetitions = 0
        new_interval = 1
        new_ease = max(1.3, ease - 0.2)
    if grade >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitons == 1:
            new_interval = 6
        else new_interval = round(interval * ease)
        new_repetitions = repetitions + 1
        new_ease = ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    return new_ease, new_interval, new_repetitions 
