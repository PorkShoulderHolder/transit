__author__ = 'sam.royston'
from turnstile_synch import UpdateManager

update_manager = UpdateManager(start_yr=15)
update_manager.synch_turnstiles()
update_manager.synch_locations()
update_manager.synch_gtfs()



