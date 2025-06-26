from pushbullet import Pushbullet

# Use your Pushbullet Access Token
pb = Pushbullet("key")


def send_notification(name, date, time):
    message = f"{name} marked present on {date} at {time}"
    pb.push_note("Attendance Marked ✅", message)
