import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html',
  styleUrls: ['./card.component.scss']
})
export class CardComponent {
  @Input() card: any;
  expanded = false;
  cardHeight = '100px';

  toggleCard(): void{
    this.expanded = !this.expanded;
    this.cardHeight = this.expanded ? 'auto' : '100px';
  }

  ngAfterViewInit(): void{
    if(this.expanded){
      this.cardHeight = 'auto';
    }
  }
}
