# Persistent STA helper: native CF_HDROP drag for Notes Icons Browse (Windows).
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Add-Type -ReferencedAssemblies System.Windows.Forms, System.Drawing -TypeDefinition @'
using System;
using System.Collections.Specialized;
using System.Drawing;
using System.Windows.Forms;

public class NoActivateForm : Form {
  protected override bool ShowWithoutActivation {
    get { return true; }
  }
  protected override CreateParams CreateParams {
    get {
      CreateParams cp = base.CreateParams;
      cp.ExStyle |= 0x08000000; // WS_EX_NOACTIVATE
      return cp;
    }
  }
}

public static class FileDrag {
  public static string Run(string[] paths) {
    var form = new NoActivateForm();
    form.FormBorderStyle = FormBorderStyle.None;
    form.ShowInTaskbar = false;
    form.Size = new Size(1, 1);
    form.StartPosition = FormStartPosition.Manual;
    form.Location = new Point(-32000, -32000);
    form.Opacity = 0;
    string result = "None";
    form.Shown += (s, e) => {
      var data = new DataObject();
      var files = new StringCollection();
      foreach (var p in paths) {
        if (!string.IsNullOrEmpty(p)) {
          files.Add(p);
        }
      }
      if (files.Count == 0) {
        form.Close();
        return;
      }
      data.SetFileDropList(files);
      result = form.DoDragDrop(data, DragDropEffects.Copy).ToString();
      form.Close();
    };
    Application.Run(form);
    return result;
  }
}
'@

[Console]::Out.WriteLine('ready')
[Console]::Out.Flush()

while ($true) {
  $line = [Console]::In.ReadLine()
  if ($null -eq $line -or $line -eq 'exit') {
    break
  }
  try {
    $obj = $line | ConvertFrom-Json
    $paths = @($obj.paths | ForEach-Object { [string]$_ })
    $effect = [FileDrag]::Run($paths)
    [Console]::Out.WriteLine("done $effect")
    [Console]::Out.Flush()
  } catch {
    [Console]::Out.WriteLine("error $($_.Exception.Message)")
    [Console]::Out.Flush()
  }
}
