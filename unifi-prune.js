// keep N-day worth of data
// call on unifi manager as: mongo --port=27117 < unifi-prune.js
// change dryrun to 'false', o'course
days=30;
dryrun=true;

use ace;
collectionNames = db.getCollectionNames();
for (i=0; i<collectionNames.length; i++) {
	name = collectionNames[i];
	query = null;
	if (name.indexOf('stat')==0 || name.indexOf('event')==0 || name.indexOf('alarm')==0) {
		query = {time: {$lt:new Date().getTime()-days*86400*1000}};
	}
	if (name.indexOf('session')==0) {
		query = {assoc_time: {$lt:new Date().getTime()/1000-days*86400}};
	}
	if (name.indexOf('user')==0) {
		query = {last_seen: {$lt:new Date().getTime()/1000-days*86400}};
	}

	if (query) {
		count = db.getCollection(name).find(query).count();
		print((dryrun ? "[dryrun] " : "") + "pruning " + count + " entries from " + name + "... ");
		if (!dryrun)
			db.getCollection(name).remove(query);
	}
}

if (!dryrun) db.repairDatabase();
