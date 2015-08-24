***************************************************************************************
If the code or this set of directions is not clear, the code does not work, or
you have any ideas for improving this code, PLEASE email me at hdoupe@yahoo.com
***************************************************************************************


This set of files consists of two main sections: radio_census and sqlite_tools

The purpose of radio_census is to gather and format data in a so that it can be 
placed in a SQLite file.  Since, the SQLite file is already given(unless you want
to wait around for a few hours and let radio_census_build gather and format the data), 
radio_census mainly serves as an interpreter of your commands from the command line.


Dependencies:
-	reverse_geocoder
https://github.com/thampiman/reverse-geocoder
-	haversine
https://github.com/mapado/haversine

Here are the flags and definitions:
	
	--std_out - print data in terminal
	--csv - print data in csv file (sep always '|')
	
	--query - execute query through Query interpreter
	--sql - statement executed by query interpreter
	--description - add description to csv file

	--population_query - get demographic totals for the queried callsigns. It could be a list
		or could be a file with callsigns where there is one callsign per line and it
		is the first item when the line is split by commas.
		python radio_census.py --population_query WNYC-FM,WTHO-FM
		python radio_census.py --population_query path/to/callsigns.txt
	--pq_variable- select demographic totals for this variable.
	
	(for these commands, see below)
	--d2 - use demographics_and_distance module
	--d2_variable - variable for condition
	--percentile - percentile for condition
	--geocode – adds geocoded variables

sqlite_tools is where the bulk of the work is done.  This component is comprised of the
modules, query and sqlite_helper.  The module, query, serves as an interface between the user and 
the SQLite database.  It reads SQL commands, formats them if necessary, and formats the
results.  The purpose of SQLite_Helper is to help Query execute commands.  It sets the table,
has some printing capabilities, and does operations on variables.

Defined Functions:

	"REGEXP('callsign',callsign)" - Routine for matching callsigns
	
	"HAVERSINE(lat1,lon1,lat2,lon2)" - calculate distance between two points (km)
	
	"PCT(v1,v2)" - divides v1 by v2 and multiplies result by 100
	
	"MEAN(*args)" - calculate mean of given arguments
	
	"DIVERSITY_RACE(*demographic variables*)" - if you use query, then all one needs
		to do to call this function is to place '{div_race}' in one's SQL query, and
		Query will evaluate it

	"DIVERSITY_AGE(*demographic variables*)" This works the same as 'DIVERSITYRACE'.  
		Just replace '{div_race}' with '{div_age}'

	"PERCENTILE('variable',variable)" Returns the percentage of values under the queried number

	"GREATERTHANPERCENTILE('variable',variable,percentile)" Returns 1 if the given 
		value is greater than or equal to the value at the given percentile, 
		returns 0 otherwise

	"EDU(license)" Returns 1 if the license appears to be affiliated with an educational
		organization, returns 0 otherwise (see code for methodology)

	"POLITICALBOUNDARY('level',latitude,longitude)" This reverse geocodes the point and 
		returns the name of the city, state, or country when level is 'name','admin1'
		or 'cc'.

The module, demographics_and_data  is given a variable and a percentile.  It uses these
parameters to find all of the radio stations that are within 100 miles of a census 
tract that satisfies the condition,'GREATERTHANPERCENTILE('variable',variable,percentile) = 1'
and their respective distances from the closest census tract satisfying the previously 
mentioned condition. Once the query is complete, it prints the stations' data to a csv file.

Examples of SQL commands:

SELECT callsign,trans_lat,trans_lon,IN_binary,NPR_binary,{div_age},{div_race}, PERCENTILE('DP0010001',DP0010001) FROM RC ORDER BY {div_age} DESC

SELECT callsign,trans_lat,trans_lon,POLITICALBOUNDARY('admin1',trans_lat,trans_lon) FROM RC WHERE IN_binary = 1 AND POLITICALBOUNDARY('admin1',trans_lat,trans_lon) = 'Georgia'

SELECT DP0010001,INTPTLAT10,INTPTLON10,{div_age},{div_race},PERCENTILE('DP0010001',DP0010001) FROM census  WHERE GREATERTHANPERCENTILE('DP0010001',DP0010001,90) = 1

Examples of Command-line usage:

python radio_census.py --query --std_out --sql  “some sql command”

python radio_census.py --population_query “WNYC-FM” --std_out --pq_variable “DP0010001” 

python radio_census.py --d2 --d2_variable “DP0010001” --percentile 90 --csv results.txt

