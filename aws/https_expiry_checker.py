#!/usr/bin/env python3
# TODO: notify something if stats pushing fails?
""" Check certificate expiry, for use in AWS Lambda

    Async is not used - the script is intended to be run 1/day, with a
    resolution of days, so async is not required

    some parts have been taken from https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/

    Parameter Store support was initially implemented, but it's not really
    usable.  A maximum of 4096 chars for a StringList, and the list is forced
    to be a comma-delimited string making it hard for human editing
"""

import sys
import os
import argparse
import textwrap
import logging
import datetime
import socket
import ssl
import boto3
from urllib3.util import parse_url

log = logging.getLogger(os.path.basename(sys.argv[0]))
# logging is not re-set as the app goes through the 'options' function, so disable debug-by-default
#log.setLevel(logging.DEBUG)
# for some reason, logging.INFO does not parse here, so using 20 instead (which is the value of logging.INFO)
log.setLevel(20)


def get_options():
    """ ... gets... options?
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''

          Usage:
            FETCH_CLOUDFRONT_ALIASES=true https-expiry-checker

            SNS_ARN=arn:aws:sns:ap-southeast-2:265577729643:paultest \\
              S3_OVERRIDE_LIST=s3://MYBUCKET/operations/ye-olde-override-list.txt \\
              FETCH_CLOUDFRONT_ALIASES=true \\
              FETCH_S3_HOSTNAMES=s3://MYBUCKET/operations/list-o-hostnames.txt \\
              ./https-expiry-checker

        This script is NOT a cert VALIDATOR - it only checks expiry times.

        This script checks for expiry of HTTPS certificates, and sends stats to
        Cloudwatch and alerts to SNS if the SNS env var is set. It will check
        all non-wildcard domains found in Cloudfront of the same AWS account,
        and also from a domain file listing stored at a nominated location on
        s3. This script is intended to be run as a lambda, which will require
        the appropriate IAM permissions.

        There is an override file on s3 for permanently disabling the checks,
        but it must be referenced as well in the env vars. You might want to
        disable checks for various reasons, such as a client's domain that is
        set up on Cloudfront but not transferred yet, or a super-legacy site
        that does not support HTTPS. Don't forget to un-disable the domain when
        appropriate.

        The locations of the hostname sources can be supplied as env vars (for
        running in lambda) or as cli args (for testing).

        FETCH_CLOUDFRONT_ALIASES  set to 'true' to fetch global list
        FETCH_S3_HOSTNAMES        set to S3 address to fetch text file list of hostnames

        S3_OVERRIDE_LIST          ignore hostnames listed in this text file

        SNS_TOPIC_ARN             if enabled, notify SNS if expiry less than DAYS
        DAYS                      threshold for SNS alerts,
                                      doesn't affect alarms set in Cloudwatch

        '''))

    parser.add_argument('-c', '--fetch-cloudfront', help='should we fetch hostnames from cloudfront? (no arg)', action='store_true')
    #parser.add_argument('-p', '--fetch-parameterstore', help='address of parameter store location with hostname list', default='')
    parser.add_argument('-s', '--fetch-s3', help='address of s3 location with hostname list', default=None)
    parser.add_argument('-n', '--sns-arn', help='publish issues to this SNS ARN', default=None)
    parser.add_argument('-d', '--days', help='threshold in days for SNS expiry warning', default=14)
    parser.add_argument('-o', '--s3-override-list', help='s3 location with textfile of hosntames to ignore', default=None)

    #log guff
    parser.add_argument('-q', '--quiet', help='sets loglevel=ERROR, good for cron', action='store_true')
    parser.add_argument('--loglevel', help='', default='INFO')
    parser.add_argument('--debug', help='overrides other loglevels', action='store_true')



    options = parser.parse_args()

    try:
        options.loglevel = getattr(logging, options.loglevel.upper())
    except:
        print("Loglevel %s unrecognised, setting to INFO" % options.loglevel)
        options.loglevel = 20
    finally:
        if options.quiet:
            options.loglevel = logging.ERROR
        if options.debug:
            print("logging set to debug")
            options.loglevel = logging.DEBUG

    ##
    ## READ ENV VARS
    ##

    try:
        if os.environ['FETCH_CLOUDFRONT_ALIASES'].lower() == 'true':
            options.fetch_cloudfront = True
    except KeyError:
        log.debug('No env var FETCH_CLOUDFRONT_ALIASES')

    #try:
    #    options.fetch_parameterstore = os.environ['FETCH_PARAMETERSTORE']
    #except KeyError:
    #    log.debug('No env var FETCH_PARAMETERSTORE')

    try:
        options.fetch_s3 = os.environ['FETCH_S3_HOSTNAMES']
    except KeyError:
        log.debug('No env var FETCH_S3_HOSTNAMES')

    if not options.fetch_cloudfront and not options.fetch_s3:
        log.error('No location supplied to fetch hostnames. Aborting')
        parser.print_help()
        sys.exit(13)

    try:
        options.s3_override_list = os.environ['S3_OVERRIDE_LIST']
    except KeyError:
        log.warning('No env var S3_OVERRIDE_LIST - no override list means there may be spam about stale/legacy sites')

    try:
        options.sns_arn = os.environ['SNS_ARN']
    except KeyError:
        log.debug('No SNS ARN set')

    try:
        options.days = int(os.environ['DAYS'])
    except KeyError:
        pass

    return options



def fetch_cloudfront_hostnames():
    """ fetch a list of all 'alias' hostnames from the same
        AWS account's CloudFront distro listing
    """

    cf_hostnames = []

    cf = boto3.client('cloudfront')

    for dist in cf.list_distributions()['DistributionList']['Items']:
        try:
            cf_hostnames += dist['Aliases']['Items']
        except:
            continue

    log.debug("CloudFront hostnames: %s", cf_hostnames)

    return cf_hostnames



def fetch_s3_hostnames(address):
    """ fetch a list of hostnames from the s3 location nominated
        in the env var FETCH_S3_HOSTNAMES - it should reference a text file
        with one hostname per line
    """

    s3_hostnames = []

    if address.startswith('s3://'):
        address = address[5:]

    try:
        s3 = boto3.resource('s3')

        bucket, key = address.split('/', 1)
        log.debug('s3 bucket %s, key %s', bucket, key)

        obj = s3.Object(bucket, key)
        contents = obj.get()['Body'].read().decode('utf-8')
        #s3_hostnames += contents.strip('\n').split('\n')
        s3_hostnames += contents.split('\n')

    except Exception as e:
        log.error('Failed to get hostnames from s3://%s: %s', address, e)

    log.debug("S3 hostnames: %s", s3_hostnames)

    return s3_hostnames




#def fetch_parameterstore_hostnames(address):
#    ps_hostnames = []
#
#    ssm = boto3.client('ssm')
#
#    try:
#        r = ssm.get_parameter(Name=address)
#        ps_hostnames += r['Parameter']['Value'].split(',')
#    except Exception as e:
#        log.warning("Failed to get hostnames from Parameter Store '%s': %s", address, e)
#
#    return ps_hostnames




def hostname_cleanup(hostnames, override_list=None):
    """ clean out malformed domains, wildcard domains, and 'override' domains
        from the list to be checked

        the override list is read from the env var S3_OVERRIDE_LIST
    """

    newlist = []
    for line in hostnames:
        host = parse_url(line)[2]
        if host is not None:
            if override_list:
                if host in override_list:
                    log.info('Rejected overridden hostname %s', host)
                    continue

            if '*' in host:
                log.debug('Rejected wildcard hostname %s', host)
                continue

            newlist.append(host)
        else:
            log.debug('Rejected bad hostname line "%s"', line)

    return newlist




def ssl_expiry_datetime(hostname):
    """ obtain the given hostname's https cert expiry date

        filched untouched from the link in the docstring at the top
    """
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    # parse the string from the certificate into a Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)




def ssl_ttl(hostname):
    """ Get the number of days left in a cert's lifetime

        filched almost untouched from the link in the docstring at the top
    """

    expires = ssl_expiry_datetime(hostname)
    log.debug("SSL cert for %s expires at %s", hostname, expires.isoformat())

    return expires - datetime.datetime.utcnow()




def check_expiry(hostnames):
    """ runs the expiry check for each hostname, storing any errors encountered
    """

    expiry_list = []

    for host in hostnames:
        ttl = None
        try:
            ttl = ssl_ttl(host)

            log.debug('%s expiry: %s', host, ttl)

            days = ttl.days
        except Exception as e:
            log.warning('%s - issue requesting certificate: %s', host, e)
            days = -1
            expiry_list.append([host, days, e])
        else:
            expiry_list.append([host, days, None])


    return expiry_list




def push_cloudwatch_stats(expiry_list):
    """ push... cloudwatch... stats...

        stats are NOT pushed if there's an SSL error. There
        is no clean way to indicate errors with a number as we
        can have genuine negative TTLs.

        Cloudwatch alarms will need to handle 'no data' as an
        alert condition, maybe? There are also SNS topics that
        alerts can be sent through
    """

    cw = boto3.client('cloudwatch')

    for host, days, error in expiry_list:

        if error is None:
            log.debug('Pushing stats for %s', host)
            # doesn't support 'days' (only seconds or smaller), so let's use count instead
            response = cw.put_metric_data(
                Namespace='Operations',
                MetricData=[
                    {
                        'MetricName': 'HTTPS_Days_To_Expiry',
                        'Dimensions': [
                            {
                                'Name': 'Hostname',
                                'Value': host
                            }
                        ],
                        'Value': days,
                        'Unit': 'Count'
                    }
                ]
            )
        else:
            log.debug('Stats for %s not pushed due to connect issue')




def notify_sns(sns_arn, badlist):
    """ Push a warning/error through SNS re: expiry TTLs

        Two types of 'bad'
        1) expiring soon
        2) some sort of connection error

        badlist items should be a list with hostname, expiry diff in days, and if an error, the error string
    """

    sns = boto3.client('sns')
    whoami = boto3.client('sts').get_caller_identity()

    subject = "[Ops] Certificate expiry checker - issues found"

    expired_message = ""
    error_message = ""

    for item in badlist:
        hostname = item[0]
        ttl = item[1]
        error = item[2]
        #if error is not None:
        if error:
            error_message += "- %s: %s\n" % (hostname, error)
            #message = ("The hostname %s had the following error when attempting to check HTTPS certificate expiry: %s!\n\n"
            #           "To permanently disable this check, add '%s' to the override list on s3\n\n"
            #           "This message has been sent by %s"
            #          ) % (hostname, error, hostname, whoami['Arn'])
            #subject = "[Ops] Error checking the https cert expiry for '%s'" % hostname
        else:
            expired_message += "- %s certificate expires in %s days\n" % (hostname, ttl)
            #message = ("The https cert for '%s' expires in %s days\n\n"
            #           "This certificate should be updated appropriately. To permanently disable this check, add '%s' to the override list on s3\n\n"
            #           "This message has been sent by %s"
            #          ) % (hostname, ttl, hostname, whoami['Arn'])
            #subject = "[Ops] '%s' HTTPS cert expires in %s days" % (hostname, ttl)

    if expired_message:
        expired_message = "\n\nThe following certificates have been found to expire soon, and should be updated appropriately:\n\n" \
                          + expired_message
    if error_message:
        error_message = "\nThe following errors were found when attempting to check HTTPS certificates:\n\n" \
                        + error_message \
                        + "\n\n'Name or service not known' errors are usually that the domain does not exist in DNS\n" \
                        + "'Unknown protocol' errors usually relate to old or unusual protocols (eg SSL3, which is deprecated)\n" \
                        + "'Connection refused' errors usually mean the site is not listening on the HTTPS port 443\n"

    message = "Issues were found when doing an HTTPS certificate expiry check:\n\n" \
              + expired_message \
              + error_message \
              + "\n\nIf the issue cannot be fixed, then the domain check can be permanently ignored by adding the domain to the override list on s3\n\n" \
              + "This message has been sent by %s" % (whoami['Arn'])


    log.debug(message)

    try:
        response = sns.publish(TopicArn=sns_arn,
                               Message=message,
                               Subject=subject
                              )
    except Exception as e:
        log.error(e)



def lambda_handler(event, context):
    main()


def main():
    """ ... main?
    """

    options = get_options()

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    log_handler = logging.StreamHandler()
    log_handler.setLevel(options.loglevel)
    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)

    log.info("Starting to check hostnames for https certificate expiry...")
    log.debug(options)

    ##
    ## Collect hostnames to check
    ##

    hostnames = []
    if options.fetch_cloudfront:
        log.debug("fetching hostnames from cloudfront")
        hostnames += fetch_cloudfront_hostnames()

    if options.fetch_s3:
        log.debug("fetching hostnames from s3")
        hostnames += fetch_s3_hostnames(options.fetch_s3)

    #if options.fetch_parameterstore:
    #    log.debug("fetching hostnames from parameter store")
    #    hostnames += fetch_parameterstore_hostnames(options.fetch_parameterstore)

    if hostnames == []:
        log.error("No hostnames found. Aborting")
        sys.exit(15)

    ##
    ## Clean up hostname list
    ##

    override_list = None
    if options.s3_override_list:
        override_list = fetch_s3_hostnames(options.s3_override_list)

    hostnames = hostname_cleanup(hostnames, override_list=override_list)

    log.debug("Hostname list: %s", hostnames)


    ##
    ## Check the expiry TTLs
    ##

    expiry_list = check_expiry(hostnames)


    ##
    ## Post-check stats posting + alerting
    ##

    log.debug(expiry_list)
    log.info("Pushing stats to Cloudwatch...")
    push_cloudwatch_stats(expiry_list)

    if options.sns_arn:
        badlist = [x for x in expiry_list if x[1] < options.days]
        log.debug(badlist)
        if badlist:
            log.info('Notifying SNS...')
            notify_sns(options.sns_arn, badlist)
    else:
        log.warning("No SNS topic set - no alerts will be sent")



    log.info("Done.")

if __name__ == '__main__':
    main()
