import Movement

try:
    while True:
        Movement.thrower()
        
finally:
    print("done")
    Movement.close()