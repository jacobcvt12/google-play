#!/usr/bin/env bash
# Store startng time in T
T=$(date +%s)

# delete previous output
rm -f output/logs/*
rm -f output/reviews/*

# Create associative array of hotels and OTAs
declare -A hotelIDs=(
[marriott]=com.marriott.mrt
[hilton]=com.hilton.android.hilton
[starwood]=com.starwood.spg
[ihg]=com.ihg.apps.android
[booking]=com.booking
[expedia]=com.expedia.bookings
[kayak]=com.kayak.android
[airbnb]=com.airbnb.android
[tripadvisor]=com.tripadvisor.tripadvisor)

app_num=${#hotelIDs[@]}

# loop through all hotels and run python download script
for app in ${!hotelIDs[*]}
do
    echo "Downloading ${app}..."
    # Call python script on hotel to download app reviews to hotel.reviews
    python ./bin/google-play-scraper.py ${hotelIDs[$app]} \
        >> output/reviews/${app}.reviews \
        2> >(tee -a output/logs/${app}_download.log >&2)

    echo "Finish downloading ${app}..."
    echo "Waiting for 10 seconds..."

    sleep 10
done

# Store ending time in T_e
T_e=$(date +%s)

# Total time in TT
TT=$((T_e - T))

printf "Time to run %02d:%02d\n" $((TT/60%60)) $((TT%60))
