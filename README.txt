**************************************************
*
* Netcon - Network Condition Monitoring Tool
*
* by David Jeske
*
**************************************************

* What is Netcon?

Netcon is an operational machine and service monitoring tool. It
allows you to setup monitoring for machine paramaters such as CPU, and
Disk Usage, as well as services such as HTTP, and MySQL. When any of
the reported data for these services meets a set of pre-determined
triggers, the people responsible for those services can be notified.

* Why write Netcon?

Netcon is unique in that one of the primary goals is to separate the
discovery of individual errors from the notification process. Some
systems do this by layering a notification suppression system on top
of a montoring and notification system (see QOS/Giraffe). However, in
Netcon these two components understand each other and work together.

The result is simple. Instead of receiving individual notifications
about service problems, which can often include tens or hundreds of
notifications, with Netcon the user receives strictly time-periodic
updates of the system state during an incident. For example, you might
receive one page every five minutes during an incident, each one
telling you how many service failures are still pending on that
incident, followed by a page indicating that the incident is resolved
and cleared.

By indicating to Netcon the user-impact of an incident, Netcon can
report on the user-percieved impact of failures over time.

* What are the other basic features of Netcon?

- data is stored in a MySQL database
- monitoring is performed by a lightweight data-collection client
- configuration data about what to monitor is administered locally
- custom data-collection clients can be written, by merely speaking
  the Netcon protocol
- clients can (optionally) save and report data for disconnected periods
- hierarchial redundant trigger suppression

* How does Netcon work?

One way to understand Netcon is to consider the flow of monitored data
through the system. Here is a description of the cycle of data
collection through an incident notification and resolution.


  1. netcon server startup
  2. netcon client startup 
     a. checkin with server to get configuration
     b. begin monitoring, periodically reporting data to server
  3. netcon server accepts reported data from many clients
     a. for each piece of data, update the 'current' state of that
        service
     b. roll previous data into 'history'
  4. netcon server periodically checks for errors
     a. load all triggers and check against 'current' state 
     b. record any trigger state changes 
     c. for any triggered errors, add them to the active incident,
        creating one if necessary
  5. netcon server periodically handles notifications
     a. iterate through active incidents, make sure currently
        active users are watching these incidents
     c. iterate over watched incidents for each user, and 
        generate notifications (user can choose a single email,
        or a single email per incident) 
     d. deactivate incidents which have been resolved and which
        have passed their 'watch' period without any activity.
  
When the user receives a notification, that notification will indicate
the severity of the incident, and the number of failures present on
that incident. By visiting the web-interface, the user can check the
detailed information reported on the incident, as well as add notes to
the incident.

When the problem is resolved, the user must acknowledge and resolve
the incident before it will be cleared. When acknowledging, the user
can indicate the user-percieved result of the failure
(degraded-performance, degraded-functionality, inaccessability), as
well as the length of time this incident should be watched for. After
the watch timeout has expired, Netcon will clear the incident and make
it part of the incident history.

