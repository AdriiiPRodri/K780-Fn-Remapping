import subprocess

def runCommand(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def existKeyboard(result):    
    result_splitted = result.split('\n')
    for index, line in enumerate(result_splitted):    
        if 'Name="Keyboard K780"' in line:
            return index
            
    return False

def obtainDataKeyboard():
    result = runCommand(['cat', '/proc/bus/input/devices'])
    line_obj = existKeyboard(result)
    if line_obj is not False:
        result_splitted = result.split('\n')
        data_keyboard = result_splitted[line_obj-1]
        bvpe = list()
        for index, character in enumerate(data_keyboard):
            if character == '=':
                index += 1
                bvpe.append(data_keyboard[index].upper())
                index += 1
                bvpe.append(data_keyboard[index].upper())
                index += 1
                bvpe.append(data_keyboard[index].upper())
                index += 1
                bvpe.append(data_keyboard[index].upper())
                bvpe.append(' ')
        bvpe.pop()
        return bvpe
    return line_obj

def defineevdev(data):
    atributtes = ['v', 'p', 'e']
    configuration = 'b'
    # print(data)
    for character in data:
        if character != ' ':
            configuration += character
        else:
            configuration += atributtes.pop(0)
    return configuration

            
def createConfigurationFile(data, ubication_copy_udev):
    evdev = defineevdev(data)
    template = open('template_99-k780.hwdb', 'r')
    final = open('99-k780.hwdb', 'w')
    for line in template:
        final.write(line.replace('CAMBIAR', evdev))
    template.close()
    final.close()
    ubication_copy_udev += '/99-k780.hwdb'
    # runCommand(['cp', '99-k780.hwdb {}99-k780.hwdb'.format(ubication_udev)])
    # runCommand(['cp', '99-k780.hwdb {}99-k780.hwdb'.format(ubication_copy_udev)])
    runCommand(['sudo', 'cp', '99-k780.hwdb', ubication_copy_udev])
    runCommand(['rm', '99-k780.hwdb'])

def persistence(ubication_service):
    runCommand(['sudo', 'udevadm', 'hwdb', '--update'])
    runCommand(['sudo', 'udevadm', 'trigger'])
    result = runCommand(['cat', ubication_service+'/systemd-hwdb-update.service'])
    persist = open('systemd-hwdb-update.service', 'w')
    to_change = '\nConditionNeedsUpdate=/etc'
    change = '\n#ConditionNeedsUpdate=/etc'
    # print(result)
    # result = result.split('\n')
    result = result.replace(to_change, change)
    persist.write(result)
    persist.close()
    runCommand(['sudo', 'mv', ubication_service+'/systemd-hwdb-update.service', ubication_service+'/systemd-hwdb-update.service.backup'])
    runCommand(['sudo', 'cp', 'systemd-hwdb-update.service', ubication_service])
    runCommand(['rm', 'systemd-hwdb-update.service'])

def main():
    #**********************************#
    #************ EDITABLE ************#
    ubication_to_copy_udev_hwdbd = '/etc/udev/hwdb.d'
    # ubication_of_udev_hwdbd = '/home/adri/Desktop'
    # ubication_to_copy_udev_hwdbd = '/home/adri/Downloads'
    ubication_service = '/etc/systemd/system'
    #**********************************#

    data = obtainDataKeyboard()
    if data is not False:
        createConfigurationFile(data, ubication_to_copy_udev_hwdbd)
        persistence(ubication_service)

if __name__ == "__main__":
    main()