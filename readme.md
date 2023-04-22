# Kindle2Txt
Kindle2Txt is a simple program that will convert Kindle Word lookup data into a simple text file.

## Getting Started
The run parameters look like this:
    Kindle2Txt.py ([vocab_db_path]) (lang) (output_folder)

An example first run for only japanese books with the output saved in the current directory would be:
    Kindle2Txt.py "d:\system\vocabulary\vocab.db" ja .

## Notes
As long as the vocab.db path never changes, you won't need any parameters after the first run. It will keep track of the last sentence timestamp that was output, so additional runs should only output new lookups since the last run.