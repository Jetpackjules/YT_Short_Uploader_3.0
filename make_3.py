from generate import generate
from helper import times_for_next_uploads_pacific
# JUST FOR REFERENCE!:
# OUTDATED!:
# vidnames=["mc_parkour_1hr", "satisfying_10hr_claimed", "satisfying_1hr"]


# Generates 3 vids tmmrw at morning, afternoon, and night, with different vids for each...
if __name__ == "__main__":
    publishtimes = times_for_next_uploads_pacific()
    generate(pubTime=publishtimes[0], upload=True, subreddit="offmychest", read_post=True) 
    generate(pubTime=publishtimes[1], upload=True)
    generate(pubTime=publishtimes[2], upload=True, subreddit="offmychest", read_post=True)
    generate(pubTime=publishtimes[3], upload=True, subreddit="offmychest", read_post=True)
    generate(pubTime=publishtimes[4], upload=True)
    generate(pubTime=publishtimes[5], upload=True)


#TODO: ADD BAKING FOOTAGE TO BACKGROUND!! (cake not cooking)