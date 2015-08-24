from datetime import datetime
import os
import argparse


class Radio_Census(object):
	def __init__(self,target_dir,data_dir,):
		
		self.target_dir = target_dir
		self.data_dir = data_dir
		self.RC_db = ""
		self.RC_table_name = ""
		self.census_db = ""
		self.census_table_name = ""

		
	def set_dbs(self):
		self.RC_db = os.path.join(self.data_dir,"radio_census.sqlite")
		self.RC_table_name = "RC"
		if not os.path.exists(self.RC_db):
			raise Exception("missing vital data: " + self.RC_db)

		self.census_db = os.path.join(self.data_dir, "census.sqlite")
		self.census_table_name = "census"
		if not os.path.exists(self.census_db):
			print "missing: ",self.census_db
			print "going on without it..."


	def fix_excel_sheet(self,path):
		from clean import clean
		clean_path = os.path.join(self.target_dir, "clean.csv")
		tmp = os.path.join(self.target_dir, "tmp.csv")
		cl = clean()
		cl.run(path,tmp,clean_path)
		return clean_path
	
	def get_npr_list(self,npr_list):
		if npr_list:
			if isinstance(npr_list,list):
				return npr_list
			if isinstance(npr_list,basestring):
				if os.path.exists(npr_list_path):
					return open(npr_list_path).read().split(',')
		
# 		Nothing is given, hence, we will go get it.
		from radio_census.converters import pdf_to_text
		pt = pdf_to_text()
		npr_list = pt.get_npr_list()
		for item in npr_list:
			with open('npr_stations.txt','w') as f:
				f.write(item.strip() + '\n')
		return npr_list

# 	I used the following functions to add the innovaion now and NPR variables
	def boolean_add(self,row,id_variable,id_values):
		value = 0
		id_value = row[id_variable]

		if id_value in id_values:
			value = 1
		else:
			value = 0
		
		return value
	
	def txt_to_binary(self,row,id_variable):
		value = 0
		innovation_now = row['NPR']
		if innovation_now == 'YES':
			value = 1
		else:
			value = 0
		
		return value
		


def main():
	data_dir = "/Users/HANK/Documents/data_processing/data"
	target_dir = "/Users/HANK/Documents/radio_stations/sql_queries/IN"
	parser = argparse.ArgumentParser()
	parser.add_argument("--query","-q",dest = "query",action = "store_true")
	parser.add_argument("--queryfile","-qf",dest = "queryfile",default = "radio_census_query.txt")
	parser.add_argument("--sql",dest = "sql",default = "")
	parser.add_argument("--description","-dscr",dest = "description",action = "store_true")
	parser.add_argument("--std_out",dest = "std_out",action = "store_true")
	parser.add_argument("--csv",dest = "csv",default = "radio_census_results.txt")
	parser.add_argument("--d2","-d",dest = "d2",action = "store_true")
	parser.add_argument("--d2_variable","-ddv",dest = "dd_variable",default = "DP0010001")
	parser.add_argument("--percentile","-pct",dest = "percentile",default = 90)
	parser.add_argument("--population_query","-pq",dest = "population_query",default = None)
	parser.add_argument("--pq_variable","-pqv",dest="pq_variable",default = "DP0010001")
	parser.add_argument("--npr","-npr",dest="npr",action = "store_true")
	args = parser.parse_args()
	
	if args.query:
		rc = Radio_Census(target_dir,data_dir,query_permission = False, IQ = True)
		print args.sql
		if args.sql:
			from sqlite_tools.query import Query
			rc.set_dbs()
			query = Query(rc.RC_db,rc.RC_table_name)
			if os.path.exists(args.sql):
				with open(args.sql) as f:
					sqls = f.read().split('\n')
			else:
				sqls = [args.sql]
			query_start = datetime.now()
			query.query(sqls = sqls,description = args.description,std_out = args.std_out,csv = args.csv)
			query_finish = datetime.now()
			print "Query Time: ",query_finish - query_start
		else:
			rc.run()
	if args.population_query:
		
		rc = Radio_Census(target_dir,data_dir,query_permission = False, IQ = False)
		rc.set_dbs()
		
		if os.path.exists(args.population_query):
			callsigns = []
			with open(args.population_query) as f:
				for line in f:
					callsigns.append(str(line.split('|')[1]).strip())
		else:
			callsigns = str(args.population_query).split(',')

		from sqlite_tools.query import Filter,Population_Query
		
		filter = Filter(callsigns,rc.RC_db,rc.RC_table_name,'callsign')
		search_hits = filter.filter()
		filter.conn.close()
		
		pq = Population_Query(search_hits,rc.RC_db,rc.RC_table_name,rc.census_db,rc.census_table_name)
		search_hits = pq.query_tracts()
		results = pq.get_population_dict()
		
		pq_variables = str(args.pq_variable).split(',')
		
		for variable in pq_variables:
			print variable,results[variable]
		
		print "But, there's more!"
		
		for variable in pq.demographic_variables():
			print variable,results[variable]
			
		if args.csv:
			pq.print_search_hits(args.csv)
			
	if args.d2:
		from demographics_and_distance import demographics_and_distance as D2
		d2 = D2(target_dir,data_dir)
		d2.query_tracts_by_stations(demographics = args.d2_variable,percentile = args.percentile,csv = args.csv)
		
if __name__ == "__main__":
	main()
			