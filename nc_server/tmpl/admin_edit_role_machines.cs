<?cs include:"header.cs" ?>

<b>Edit Machines for Role '<?cs var:html_escape(CGI.role.name) ?>'</b><p>

<form method=post action="admin_edit_role_machines.py">
<input type=hidden name=role_id value="<?cs var:CGI.role.role_id ?>">

<table border=1 width=80% align=center>
<?cs each:agnt=CGI.agents ?>
  <tr><td width=1%><input type=checkbox <?cs if:CGI.mach_roles[agnt.mach_id] ?>CHECKED<?cs /if ?> name="mach.<?cs var:agnt.mach_id ?>" value="1"></td>
      <td width=30%><?cs var:agnt.machine.name ?></td>
      <td><?cs var:agnt.last_check_in.string ?>&nbsp;</td>
 </tr>

<?cs /each ?>

<tr><td colspan=3 bgcolor=#eeeeee align=center>
<input type=submit name="Action.Save" value="Save &gt;&gt;">
</td></tr>
</table>

</form>



<?cs include:"footer.cs" ?>