import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf import transformations
import math

ranges_ = { 
    'right' : 0,
    'fright': 0,
    'front' : 0,
    'fleft' : 0,
    'left'  : 0,
}

state_   = None
states_ = { 
    0 : 'finding wall',
    1 : 'turning left',
    2 : 'following wall',
    3 : 'turning right',
}


def scanCallback(msg):
    global ranges_
    ranges_ = { 
        'right'  : min(min(msg.ranges[240:288]), 10),
        'fright' : min(min(msg.ranges[288:336]), 10),
        'front'  : min(min(msg.ranges[0:24]), min(msg.ranges[336:360]), 10),
        'fleft'  : min(min(msg.ranges[24:72]), 10),
        'left'   : min(min(msg.ranges[72:120]), 10),
    }
    
    action()


def changeState(state):
    global state_, states_
    if(state is not state_):
        print "Wall Follower now %s" % (states_[state])
        state_ = state


def action():
    global ranges_
    ranges = ranges_
    t = Twist()
    d = 0.8
    description = ''

    if ranges['front'] > d and ranges['fleft'] > d and ranges['fright'] > d and ranges['right'] < d:
        description = 'case 1 - right'
        changeState(3)
    elif ranges['front'] < d and ranges['fleft'] > d and ranges['fright'] > d:
        description = 'case 2 - front'
        changeState(1)
    elif ranges['front'] > d and ranges['fleft'] < d and ranges['fright'] > d:
        description = 'case 3 - fleft'
        changeState(0)
    elif ranges['front'] > d and ranges['fleft'] > d and ranges['fright'] < d:
        description = 'case 4 - fright'
        changeState(2)
    elif ranges['front'] < d and ranges['fleft'] < d and ranges['fright'] > d:
        description = 'case 5 - front fleft'
        changeState(1)
    elif ranges['front'] < d and ranges['fleft'] > d and ranges['fright'] < d:
        description = 'case 6 - front fright'
        changeState(1)
    elif ranges['front'] < d and ranges['fleft'] < d and ranges['fright'] < d:
        description = 'case 7 - front fleft fright'
        changeState(1)
    elif ranges['front'] > d and ranges['fleft'] < d and ranges['fright'] < d:
        description = 'case 8 - fleft fright'
        changeState(0)
    elif ranges['front'] > d and ranges['fleft'] > d and ranges['fright'] > d:
        description = 'case 9 - none'
        changeState(0)
    else:
        description = 'case 0 - error'


# Prepare to publish topic
rospy.init_node('wallFollower')
scan_sub = rospy.Subscriber('/scan', LaserScan, scanCallback)
odom_sub = rospy.Subscriber('odom', Odometry, odomCallback)
vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
rate = rospy.Rate(10)

# loop until Ctrl+C
while not rospy.is_shutdown():
    if state_ == None:
        print('waiting...')
    else:
        t = Twist()
        if state_ == 0:
            t.linear.x = 0.2
            t.angular.z = -0.2
        elif state_ == 1:
            t.angular.z = 0.25
        elif state_ == 2:
            t.linear.x = 0.3
        elif state_ == 3:
            t.angular.z = -0.35
        else:
            print('ERROR - state not found')
        vel_pub.publish(t)
    rate.sleep()