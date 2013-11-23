#!/usr/bin/env bash

folder="j-archive"
if [[ ! -d $folder ]]
then
	echo "Making $folder"
	mkdir "$folder"; cd "$folder"

	echo "Downloading game files"
	for i in {1..4321}
	do
		curl -v -o "$i.html" "http://j-archive.com/showgame.php?game_id=$i"
		sleep 5s # Remember to be kind to the server
	done
	cd .. # Leave the folder
fi

script="parser.py"
if [[ ! -x $script ]]
then
	echo "Setting script as executable"
	chmod +x "$script"
fi

echo "Running script"
duration=`(time ./$script) 2>&1 | grep real | cut -f2`
echo "Took $duration"
