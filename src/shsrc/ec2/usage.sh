# help message for ec2
# @params
# $1: action_type

function usage() {
  local action="$1"
  if [[ -z "$action" ]]; then
    echo "usage: faws ec2 [-h] {ssh,stop,terminate} ...\n"
    echo "perform actions on the selected instance\n"
    echo "positional arguments:"
    echo "  {ssh,stop,terminate}\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
  elif [[ "$action" == 'ssh' ]]; then
    echo "usage: faws ec2 ssh [-h] [-r] [-p] [-w] [-u]\n"
    echo "ssh into the selected instance\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
    echo "  -r\t\tselect a different region rather than using the default region"
    echo "  -p PATH\tspecify a different path than config for the location of the key pem file"
    echo "  -w\t\tpause the program and wait for instance to be running if it is currently stopped"
    echo "  -u NAME\tspecify a different username used to ssh into the instance, default is ec2-user"
  elif [[ "$action" == 'reboot' ]]; then
    echo "usage: faws ec2 reboot [-h] [-r] [-w]\n"
    echo "reboot the selected instance\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
    echo "  -r\t\tselect a different region rather than using the default region"
  else
    echo "usage: faws ec2 $action [-h] [-r] [-w]\n"
    echo "$action the selected instance\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
    echo "  -r\t\tselect a different region rather than using the default region"
    echo "  -w\t\tpause the program and wait for instance $action complete"
  fi
}
