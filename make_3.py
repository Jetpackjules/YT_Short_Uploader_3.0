from generate import generate
import helper
# JUST FOR REFERENCE!:
# OUTDATED!:
# vidnames=["mc_parkour_1hr", "satisfying_10hr_claimed", "satisfying_1hr"]


# Generates 3 vids tmmrw at morning, afternoon, and night, with different vids for each...
if __name__ == "__main__":
    publishtimes = helper.times_for_tomorrow_pacific()
    # generate(pubTime=publishtimes[0], upload=True) 
    generate(pubTime=publishtimes[1], upload=True)
    generate(pubTime=publishtimes[2], upload=True)

    # publishtimes = helper.times_for_tomorrow_pacific()
    # generate(pubTime=publishtimes[0], upload=True)
    # generate(pubTime=publishtimes[1], upload=True)
    # generate(pubTime=publishtimes[2], upload=True)

#TODO: ADD BAKING FOOTAGE TO BACKGROUND!! (cake not cooking)