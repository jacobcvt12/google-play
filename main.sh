#!/usr/bin/env bash

# create output directories if they don't exist
mkdir -p output/{logs,reviews}

# delete previous output
rm -f output/logs/*
rm -f output/reviews/*

# Create associative array apps and ids
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
        2> >(tee -a output/logs/${app}_download.log >&2) \
        | sed "s/^/$app|/g" > output/reviews/${app}.reviews 

    echo "Finish downloading ${app}..."
    echo "Waiting for 30 seconds..."

    sleep 30
done
