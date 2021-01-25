import asyncio
import json
import random

actions = [
    {
        "actions": {
            "walk": {
                "payload": {
                    "duration": 120,
                    "min-duration": 90
                }
            }
        }
    },
    {
        "actions": {
            "spotify": {
                "payload": {
                    "url": "https://open.spotify.com/playlist/6gCC8kozvUlLGTzl2YO2MR"
                }
            }
        }
    },
    {
        "actions": {
            "sleep": {
                "payload": {
                    "duration": 30,
                    "min-duration": 25,
                    "max-duration": 40
                }
            }
        }
    },
    {
        "actions": {
            "talk": {
                "payload": {
                }
            }
        }
    },
    {
        "actions": {
            "walk": {
                "payload": {
                    "duration": 120,
                    "min-duration": 90
                }
            },
            "spotify": {
                "payload": {
                    "url": "https://open.spotify.com/playlist/6gCC8kozvUlLGTzl2YO2MR"
                }
            }
        }
    },
    {
        "actions": {
            "walk": {
                "payload": {
                    "duration": 120,
                    "min-duration": 90
                }
            },
            "talk": {
                "payload": {
                }
            }
        }
    },
    {
        "actions": {
            "noop": {
                "payload": {
                }
            }
        }
    },
    {
        "actions": {
            "emergency": {
                "payload": {
                    "phone-number": "+48123123123"
                }
            }
        }
    }
]

if __name__ == "__main__":
    output = {}
    with open("actions.json", "w") as write_file:
        for x in ['1','2','3','4']:
            for y in ['1','2','3','4']:
                for z in ['1','2','3','4']:
                    for v in ['1','2','3','4']:
                        key = x+y+z+v
                        if x=='2' and y=='2':
                            action = 6
                        elif x=='4' or y=='4':
                            action = 7
                        else:
                            action = random.randint(0, 5)
                        output.update(dict([(key,actions[action])]))
        json.dump(output, write_file, indent=4)


    with open("actions.json", "r") as read_file:
        data = json.load(read_file)
    print(data['4422'])