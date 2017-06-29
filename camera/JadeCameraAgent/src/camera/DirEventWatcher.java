package camera;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.function.Consumer;

import org.json.JSONException;
import org.json.JSONObject;

import jade.core.behaviours.SimpleBehaviour;

public class DirEventWatcher extends SimpleBehaviour {	
	
	private static final long serialVersionUID = 2753511849303718365L;
	
	private String dir;
	private Consumer<JSONObject> callback;
	private boolean isDone;

	public DirEventWatcher(String dir, Consumer<JSONObject> callback) {
		this.dir = dir;
		this.callback = callback;
		this.isDone = false;
		System.out.println(dir);
	}
	
	@SuppressWarnings("unchecked")
	@Override
	public void action() {
		System.out.println("action: " + dir);
		try {
			Path dir = Paths.get(this.dir);
			WatchService watcher = FileSystems.getDefault().newWatchService();
		    dir.register(watcher, java.nio.file.StandardWatchEventKinds.ENTRY_CREATE);
		    
		    for (;;) {		    	
		    	try {

				    WatchKey key;
				    try {
				        key = watcher.take();
				    } catch (InterruptedException x) {
				        return;
				    }
	
				    for (WatchEvent<?> event: key.pollEvents()) {
				        WatchEvent.Kind<?> kind = event.kind();
	
				        if (kind == java.nio.file.StandardWatchEventKinds.OVERFLOW) {
				            continue;
				        }
	
				        WatchEvent<Path> ev = (WatchEvent<Path>)event;
				        Path filename = ev.context();				            
				        filename = Paths.get(dir.toString(), filename.toString());
				        String newFileContent = new String(Files.readAllBytes(filename));
				        JSONObject obj = new JSONObject(newFileContent);
				        
				        callback.accept(obj.getJSONArray("images").getJSONObject(0));
				    }
	
				    boolean valid = key.reset();
				    if (!valid) {
				        break;
				    }
			    
			    } catch (IOException | JSONException x) {
				    System.err.println(x);
				}
			}
		    
		} catch (IOException x) {
		    System.err.println(x);
		}
		
		System.out.println("End: " + this.dir);
		isDone = true;
	}

	@Override
	public boolean done() {
		return isDone;
	}
}