<?cs include:"header.cs" ?>

admin edit config<p>

<form action="admin_edit_config.py" method=post>
<input type=hidden name=role_id value="<?cs var:CGI.role.role_id ?>">

<table border=1>
<?cs each:rc=CGI.role_config ?>
 <tr>
   <td><input type=checkbox name="rows.<?cs var:rc.role_config_id ?>.delete" value=1>Delete</td>
            
   <td><input type=text name="rows.<?cs var:rc.role_config_id ?>.collector"
                      value="<?cs var:html_escape(rc.collector) ?>"></td>
   <td><input type=text name="rows.<?cs var:rc.role_config_id ?>.collector_config"
                      value="<?cs var:html_escape(rc.collector_config) ?>"></td>
   <input type=hidden name="rows.<?cs var:rc.role_config_id ?>.role_config_id"
           value="<?cs var:rc.role_config_id ?>">
 </tr>
<?cs /each ?>
<tr><td colspan=3 bgcolor=#eeeeee>Add New:</td></tr>
<tr><td>&nbsp;</td>
    <td><input type=text name="rows.n0.collector" value="">
    <Td><input type=text name="rows.n0.collector_config" value="">
 </tr>

</table>
<p>

<input type=submit name="Action.Save" value="Save &gt;&gt;">

</form>



<?cs include:"footer.cs" ?>