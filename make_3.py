from generate import generate
import helper
# JUST FOR REFERENCE!:
vidnames=["mc_parkour_1hr", "satisfying_10hr_claimed", "satisfying_1hr"]


# Generates 3 vids tmmrw at morning, afternoon, and night, with different vids for each...
if __name__ == "__main__":
    publishtimes = helper.times_for_tomorrow_pacific()
    generate(vidName = "mc_parkour_1hr", pubTime=publishtimes[0])
    generate(vidName = "mc_parkour_1hr", pubTime=publishtimes[1])
    generate(vidName = "satisfying_1hr", pubTime=publishtimes[2])


