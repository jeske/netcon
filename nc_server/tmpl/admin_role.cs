<?cs include:"header.cs" ?>

<b>Admin Role '<?cs var:CGI.role.name ?>'</b> <a href="admin_edit_role.py?role_id=<?cs var:CGI.role.role_id ?>">Edit</a> &nbsp; &nbsp; <a href="admin_delete_role.py?role_id=<?cs var:CGI.role.role_id ?>">Delete</a><p> 

<b>collector config</b> <a href="admin_edit_config.py?role_id=<?cs var:CGI.role.role_id ?>">Edit</a> 
<table border=1>
<?cs each:rc=CGI.role_config ?>
  <tr>
   <Td><?cs var:rc.collector ?></td>
   <td><?cs var:rc.collector_config ?></td>
  </tr>
<?cs /each ?>
</table>


<p>
<b>triggers</b> <a href="admin_edit_trigger.py?create=1&role_id=<?cs var:CGI.role.role_id ?>">create new</a><br>
<table border=1>
<?cs each:trig=CGI.role_triggers ?>
 <tr>
   <td><A href="admin_edit_trigger.py?trigger_id=<?cs var:trig.trigger_id ?>">Edit</a></td>
   <td><b><?cs var:trig.name ?></b></td> 
   <td><?cs var:trig.level ?></td>
   <td><?cs var:CGI.services[trig.serv_id].namepath ?>:<?cs var:CGI.services[trig.serv_id].type ?></td>
   <td><?cs var:html_escape(TestTypes[trig.test_type]) ?> '<?cs var:trig.tvalue ?>'</td>
   <td>For '<?cs var:trig.source_pattern ?>'</td>
 </tr>
<?cs /each ?>

</table>

<p>

<b>machines</b> <a href="admin_edit_role_machines.py?role_id=<?cs var:CGI.role.role_id ?>">edit machines</a><br>
<table border=1>
<?cs each:mach=CGI.role_machines ?>
 <tr><Td><?cs var:mach.name ?></td></tr>
<?cs /each ?>
</table>



<?cs include:"footer.cs" ?>
