#!/bin/bash
echo "Setting wallpaper to $1";
dconf write /org/mate/desktop/background/picture-filename "'$1'";