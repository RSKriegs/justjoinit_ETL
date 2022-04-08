#Fill the lines in brackets <<>> with appropriate data
$env:path="$env:Path;<<Path>>"
python justjoinit_etl.py --path <<PATH>> --load Y --project_id <<PROJECT_ID>> --table_id <<TABLE_ID>> --google_path <<GOOGLE_PATH>>
Out-File -FilePath <<LOG>>
Start-Transcript -Path <<TRANSCRIPT>>