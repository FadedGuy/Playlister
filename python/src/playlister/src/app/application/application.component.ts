import { Component, OnInit } from '@angular/core';
import { ApplicationService } from './application.service';


@Component({
  selector: 'app-application',
  templateUrl: './application.component.html',
  styleUrls: ['./application.component.scss']
})
export class ApplicationComponent implements OnInit{
  message: string = "";
  urlText: string="";
  cards = [];
  
  constructor(private appSvc: ApplicationService){}
  
  ngOnInit(): void {
    this.receive();
  }

  send(){
    const expr = /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)|youtu\.be\/)([-_a-zA-Z0-9]{11})/;
    
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
          this.receive();
        }
      })
    }
    this.message = "Invalid input";
  }

  receive(){
    this.appSvc.retrieveURL().subscribe({
      next: (c) => {
        console.log(c);
        this.cards= JSON.parse(c);
        this.message = "nice";
      },
      error: (c) => {
        console.error("bad");
        this.message = "bad";
      },
      complete: () => {
        console.log("finish");
        this.message = "finish";
      }
    })
  }
}
