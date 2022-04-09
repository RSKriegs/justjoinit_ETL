#Fill the lines in brackets <<>> with appropriate data
$env:path="$env:Path;<<Path>>"
Start-Transcript -Path <<TRANSCRIPT>>
python justjoinit_etl.py --path <<PATH>> --load Y --mode replace --project_id <<PROJECT_ID>> --table_id <<TABLE_ID>> --google_path <<GOOGLE_PATH>>
