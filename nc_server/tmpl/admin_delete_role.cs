<?cs include:"header.cs" ?>

<b>Delete role <?cs var:html_escape(CGI.role.name) ?></b>

<form action="admin_delete_role.py" method=post>
<input type=hidden name=role_id value="<?cs var:CGI.role.role_id ?>">

<p>

<table>

<tr><td bgcolor=#eeeeee colspan=2 align=center>
<input type=submit name="Action.Delete" value="Delete">
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<input type=submit name="Action.Cancel" value="Cancel &gt;&gt;">
</td></tr>
</table>

</form>

<?cs include:"footer.cs" ?>