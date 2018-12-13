# Filling the DB
#### setup
The folder structure should be
```
some_mp3_files/AlbumA/*.mp3
some_mp3_files/ALbumB/*.mp3
```
these are the albums i downloaded/extracted into some_mp3_files. idc about any of the music, just saying

http://freemusicarchive.org/music/A_A_Aalto/The_West/
http://freemusicarchive.org/music/Dee_Yan-Key/Requiem_for_String_Quartet_in_C_minor/
http://freemusicarchive.org/music/Meavy_Boy/EP_71_to_20/
http://freemusicarchive.org/music/Ask%20Again/Drama_King_Action_Orchestra/
http://freemusicarchive.org/music/Scott_Holmes/Corporate__Motivational_Music_2/
http://freemusicarchive.org/music/The_Franks/Un_EP/

#### running the script
1. start the ApplicationContainer, the server must be running
2. run the script (unix)
```
cd mp3extractor
pipenv run python run main.py
```