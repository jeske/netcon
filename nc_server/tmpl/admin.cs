<?cs include:"header.cs" ?>

<b>Admin</b><p>

<b>roles</b><br>
<table border=1>
<?cs each:role=CGI.roles ?>
  <tr><td><a href="admin_role.py?role_id=<?cs var:role.role_id ?>"><?cs alt:role.name ?>(no name)<?cs /alt ?></a></td><td><?cs var:role.machine_count ?></tr>
<?cs /each ?>
</table>

<?cs include:"footer.cs" ?>
