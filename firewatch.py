import ConfigParser
import time
import os


Config = ConfigParser.ConfigParser()
Config.read('firewatch.cfg')
sensor = Config.get('cpu', 'sensor')
start = int(Config.get('cpu', 'start'))
cores = int(Config.get('cpu', 'cores'))
temp_type = int(Config.get('temp', 'type'))


def get_core_temp(cpu_sensor, core):
    path = cpu_sensor % core
    sensor_file = open(path)
    temp = int(sensor_file.readline().rstrip('\n'))
    sensor_file.close()
    return temp


def get_cpu_temp(cpu_sensor, cpu_start=0, cpu_cores=1, cpu_temp_type=0):
    temps = []
    for i in xrange(start, cpu_cores+cpu_start):
        temps.append(get_core_temp(cpu_sensor, i))
        pass
    # return temp
    if cpu_temp_type == 2:
        return sum(temps)/len(temps)
    elif cpu_temp_type == 1:
        return min(temps)
    else:
        return max(temps)


def handle_temp_change(current, deviation, t_range):
    set_temp_wallpaper(current, deviation, t_range)


def set_temp_wallpaper(temp, deviation, t_range):
    deviation_threshold=float(Config.get('temp', 'deviation_threshold')) or 0.5
    if t_range == 1:
        # CPU is hotter than average
        if int(Config.get('wallpaper', 'compose')) == 1:
            # compose wallpaper
            compose_wallpaper(Config.get('wallpaper', 'warm'), Config.get('wallpaper', 'normal'), Config.get('wallpaper', 'output'), int(deviation*100))
        else:
            # switch wallpaper
            if deviation >= deviation_threshold:
                set_wallpaper(Config.get('wallpaper', 'warm'))
            else:
                set_wallpaper(Config.get('wallpaper', 'normal'))

    else:
        # CPU is cooler than average
        # CPU is hotter than average
        if int(Config.get('wallpaper', 'compose')) == 1:
            # compose wallpaper
            compose_wallpaper(Config.get('wallpaper', 'normal'), Config.get('wallpaper', 'cool'), Config.get('wallpaper', 'output'), int(deviation * 100))
        else:
            # switch wallpaper
            if 1-deviation >= deviation_threshold:
                set_wallpaper(Config.get('wallpaper', 'cool'))
            else:
                set_wallpaper(Config.get('wallpaper', 'normal'))


def set_wallpaper(filepath):
    directory = os.path.dirname(os.path.abspath(__file__))
    os.system('bash set_wallpaper.sh %s/%s' % (directory, filepath))


def compose_wallpaper(top, bottom, output, alpha):
    os.system('composite -blend %i %s %s %s' % (alpha, top, bottom, output))
    set_wallpaper(output)


def main():
    current = get_cpu_temp(sensor, start, cores, temp_type)
    low = min(float(Config.get('temp', 'low')), current)
    high = max(float(Config.get('temp', 'high')), current)
    normal = float(Config.get('temp', 'normal'))
    # normal = (low+high)/2
    distance = abs(current-normal)
    deviation = distance / (high - normal)
    if current < normal:
        deviation = 1 - deviation
        temp_range = 0
    else:
        temp_range = 1
    print "low=%f"%low
    print "high=%f" % high
    print "normal=%f" % normal
    print "distance=%f" % distance
    return current, deviation, temp_range

last_temp = None
last_threshold_temp = None
change = 0
while 1:
    Config.read('firewatch.cfg')
    print(chr(27) + "[2J")
    threshold = float(Config.get('temp', 'threshold'))
    current_temp, current_deviation, temp_range = main()
    if last_temp is None or last_threshold_temp is None:
        last_threshold_temp = current_temp
        handle_temp_change(current_temp, current_deviation,temp_range)
    else:
        change = current_temp-last_threshold_temp
        if abs(change) > threshold:
            handle_temp_change(current_temp, current_deviation, temp_range)
            last_threshold_temp = current_temp
    last_temp = current_temp

    print "current_temp=%f" % current_temp
    print "last_temp=%f" % last_threshold_temp
    print "deviation=%f" % current_deviation
    print "deviation_threshold=%s" % Config.get('temp', 'deviation_threshold')
    print "threshold=%f" % threshold
    if change != 0:
        print "change=%f" % change
    if temp_range == 1:
        print "cpu is hot"
    else:
        print "cpu is cool"
    sleep = min(1, float(Config.get('cpu', 'sleep')))
    time.sleep(sleep)

exit(0)
