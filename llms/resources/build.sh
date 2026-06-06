#!/bin/bash

selected=0
options=("1. Run Server" "2. Run Client")

show_menu() {
    printf "\033[H\033[J"
    echo "Select an option (Up/Down to move, Enter to select):"
    for i in "${!options[@]}"; do
        if [ "$i" -eq "$selected" ]; then
            echo " > ${options[$i]}"
        else
            echo "   ${options[$i]}"
        fi
    done
}

show_menu

while true; do
    read -rsn1 key
    if [[ $key == $'\x1b' ]]; then
        read -rsn2 key
        if [[ $key == "[A" ]]; then
            ((selected--))
            [ $selected -lt 0 ] && selected=$((${#options[@]} - 1))
        elif [[ $key == "[B" ]]; then
            ((selected++))
            [ $selected -ge ${#options[@]} ] && selected=0
        fi
        show_menu
    elif [[ $key == "" ]]; then
        break
    fi
done

printf "\033[H\033[J"
case $selected in
    0)
        echo "Launching Server..."
        cd server && python3 main.py
        ;;
    1)
        echo "Launching Client..."
        cd client/desktop && python3 main.py
        ;;
esac
