import time, json

SAMPLE_CONFIG = {
    'general': ['system_info', 'drives_info', 'memory_info', 'network_info'],
    'dir_size': ['/var/www'],
    'command_output': [
        {
            'name': 'home listing',
            'command_vector': ['bash', '-c', 'ls -alh $HOME']
        }
    ],
    'regex_match_command_output': [
        {
            'name': 'home listing',
            'command_vector': ['bash', '-c', 'ls -alh $HOME'],
            'pattern': "\\d{2}:\\d{2}"
        }
    ],
    'regex_search_command_output': [
        {
            'name': 'home listing',
            'command_vector': ['bash', '-c', 'ls -alh $HOME'],
            'pattern': "\\d{2}:\\d{2}"
        }
    ]
}


def get_command_output(command_vector):
    from subprocess import Popen, PIPE
    p = Popen(command_vector, stdout=PIPE)
    output, ret = p.communicate()
    return output.decode(errors="replace")


def regex_match_command_output(command_vector, pattern):
    import re
    output = get_command_output(command_vector)
    return re.match(pattern, output) is not None


def regex_search_command_output(command_vector, pattern):
    import re
    output = get_command_output(command_vector)
    return re.search(pattern, output) is not None


def dir_size(path):
    from pathlib import Path
    root_directory = Path(path)
    return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())


def system_info():
    import socket, time, platform, psutil, uuid

    return {
        "hostname": socket.gethostname(),
        "platform_name": platform.system(),
        "platform_version": platform.release(),
        "uuid": uuid.getnode(),
        "uptime": int(time.time() - psutil.boot_time()),
        "cpu_count": psutil.cpu_count(),
        "cpu_usage": psutil.cpu_percent(interval=1),

    }


def drives_info():
    import psutil
    mounts_stats = psutil.disk_partitions()
    drives = []
    for ms in mounts_stats:
        try:
            disk = {
                "name": ms.device,
                "mount_point": ms.mountpoint,
                "type": ms.fstype,
                "total_size": psutil.disk_usage(ms.mountpoint).total,
                "used_size": psutil.disk_usage(ms.mountpoint).used,
                "percent_used": psutil.disk_usage(ms.mountpoint).percent
            }

            drives.append(disk)
        except:
            pass
    return drives


def memory_info():
    import psutil
    stats = psutil.virtual_memory()
    return {
        'memory_total': stats.total,
        'memory_used': stats.used,
        'memory_used_percent': stats.percent
    }


def network_info():
    import psutil, time

    interfaces = []
    nics = psutil.net_if_addrs()
    for interface in nics:
        snics = []

        for snic in nics[interface]:
            snics.append({
                'family': str(snic.family),
                'address': snic.address,
                'netmask': snic.netmask,
            })
        nics.append({
            'interface': interface,
            'snics': snics
        })
    counter0 = psutil.net_io_counters()
    time.sleep(1)
    counter1 = psutil.net_io_counters()

    return {
        "network_up": max(0, counter1.bytes_sent - counter0.bytes_sent),
        "network_down": max(0, counter1.bytes_recv - counter0.bytes_recv),
        "network_cards": interfaces,
    }


def main(config=None):
    config = config or SAMPLE_CONFIG
    res = {
        'timestamp': time.time(),
    }

    # General System Info
    if 'general' in config:
        for info in config['general']:
            if info == 'system_info':
                res['system_info'] = system_info()
            elif info == 'drives_info':
                res['drives'] = drives_info()
            elif info == 'memory_info':
                res['memory'] = memory_info()
            elif info == 'network_info':
                res['network']: network_info()

    # Directory Sizes:
    if 'dir_size' in config:
        res['dir_sizes'] = {}
        for dir in config['dir_size']:
            res['dir_sizes'][dir] = dir_size(dir)

    # Command outputs
    if 'command_output' in config:
        res['command_outputs'] = {}
        for obj in config['command_output']:
            res['command_outputs'][obj['name']] = get_command_output(obj['command_vector'])

    # Command Outputs Match
    if 'regex_match_command_output' in config:
        res['regex_match_command_output'] = {}
        for obj in config['regex_match_command_output']:
            res['regex_match_command_output'][obj['name']] = regex_match_command_output(obj['command_vector'],
                                                                                        obj['pattern'])

    # Command Outputs Search
    if 'regex_search_command_output' in config:
        res['regex_search_command_output'] = {}
        for obj in config['regex_search_command_output']:
            res['regex_search_command_output'][obj['name']] = regex_search_command_output(obj['command_vector'],
                                                                                         obj['pattern'])

    print(json.dumps(res, indent=3))


if __name__ == "__main__":
    try:
        import sys

        config_path = sys.argv[1]
    except:
        config_path = None
    if config_path:
        with open(config_path) as fin:
            config = json.load(fin)
        main(config)
    else:
        main()
