import { Component } from '@angular/core';
import { ApplicationService } from './application.service';


@Component({
  selector: 'app-application',
  templateUrl: './application.component.html',
  styleUrls: ['./application.component.scss']
})
export class ApplicationComponent {
  message: string = "";
  urlText: string="";
  
  constructor(private appSvc: ApplicationService){}
  
  send(){
    const expr = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/;
    
    if(this.urlText.match(expr)){
      this.appSvc.sendURL(this.urlText).subscribe({
        next: () => {
          console.log("nice");
          this.message = "nice";
        },
        error: () => {
          console.error("bad");
          this.message = "bad";
        },
        complete: () => {
          console.log("finish");
          this.message = "finish";
        }
      })
    }
    this.message = "Invalid input";
  }

  receive(){
    this.message = this.urlText + "1";
  }
}
