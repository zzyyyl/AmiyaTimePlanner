from datetime import datetime
from utils import loadConfig, addEvent

def main():
    time_schedule = loadConfig()
    while True:
        try:
            addEvent(input_string=input("Add event:"),
                     time_schedule=time_schedule,
                     now=datetime.now())
        except (KeyboardInterrupt, EOFError):
            break
        except AssertionError as e:
            print(e.__repr__())
            raise
        except EOFError:
        	break
        except Exception as e:
            raise

if __name__ == '__main__':
    main()
    print("Exit.")
