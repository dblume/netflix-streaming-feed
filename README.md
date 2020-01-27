[![License](https://img.shields.io/badge/license-MIT_license-blue.svg)](https://raw.githubusercontent.com/dblume/netflix-streaming-feed/master/LICENSE.txt)
![python3.x](https://img.shields.io/badge/python-3.x-green.svg)

## Netflix Streaming Activity Feed

You can create a streaming activity feed with this script. Activity feeds are
records of the things you've done. In this case, it's a list of shows
you've watched.

Activity feeds can be used to collect data for lifestreaming and for Quantified
Self projects.

## Getting Started

1. Rename netflix\_streaming\_feed.cfg.sample to netflix\_streaming\_feed.cfg.
2. Customize the variables in netflix\_streaming\_feed.cfg. (More on this below.)
3. Set up a cronjob that runs netflix\_streaming\_feed.py once every day.

You can specify an output file for logs with the -o flag, like so:

    ./netflix_streaming_feed.py -o netflix_streaming_feed.log

The feed will be written to the filename specified in netflix\_streaming\_feed.cfg, in this
example, it'd be an RSS feed named "netflix\_streaming.xml"

## How it works

It downloads your entire user activity history from Netflix, and then makes
an activity feed of the last few shows you streamed.

## Customizing netflix\_streaming\_feed.cfg

The configuration file looks like this:

    [main]
    email = user@example.org
    password = correcthorsebatterystaple
    profile_token = GET_ME_FROM_HTML_SOURCE
    user_guid = GET_ME_FROM_/viewingactivity_SOURCE
    [feed]
    filename = netflix_streaming.xml
    href = http://domain.org/%(filename)s
    title = My Netflix Streaming Activity Feed

Replace email and password with your Netflix email and password. You'll have to
find your profile\_token and user\_guid from the Netflix HTML. Set the
feed filename, location, and title as you like.

### Protect your password

If netflix\_streaming\_feed.cfg is present on your server that's serving the RSS feed, be sure
to deny access to it. If you have a .htaccess file, you can do so with

    <Files ~ "\.cfg$">
    Order allow,deny
    Deny from all
    </Files>


## An example feed

Here's [an example feed](http://feed.dlma.com/netflix_streaming.xml). It [meets RSS validation requirements](https://validator.w3.org/feed/check.cgi?url=http%3A//feed.dlma.com/netflix_streaming.xml). &check;

## Is it any good?

Not yet. It needs a valid Auth URL to work.

## Licence

This software uses the [MIT license](https://raw.githubusercontent.com/dblume/netflix-streaming-feed/master/LICENSE.txt)
