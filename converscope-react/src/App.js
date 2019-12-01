import React from 'react';
import './App.css';
import {Line} from 'react-chartjs-2';

function ConversationPill(props) {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="">{props.group_name}</h5>
        <div className="">{props.message_count} messages</div>
        <div className="text-muted small"><ul className="participants">{props.participants.length > 2 ? props.participants.map((name) => <li key={props.c_id + name}>{name}</li>) : ""}</ul></div>
        <Line data={{
          labels: props.x_axis,
          datasets: [{      label: '',
      fill: false,
      lineTension: 0.1,
      backgroundColor: 'rgba(75,192,192,0.4)',
      borderColor: 'rgba(75,192,192,1)',
      borderCapStyle: 'butt',
      borderDash: [],
      borderDashOffset: 0.0,
      borderJoinStyle: 'miter',
      pointBorderColor: 'rgba(75,192,192,1)',
      pointBackgroundColor: '#fff',
      pointBorderWidth: 1,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: 'rgba(75,192,192,1)',
      pointHoverBorderColor: 'rgba(220,220,220,1)',
      pointHoverBorderWidth: 2,
      pointRadius: 1,
      pointHitRadius: 10,
data: props.count_by_day}]
        }} />

      </div>
    </div>
  );
}

class ConversationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: [],
      dates: [],
    };
  }

  componentDidMount() {
    fetch("http://localhost:5000/api/conversations")
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            items: result.conversations,
            dates: result.dates,
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, items, dates } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
          items.map(item => (
            <ConversationPill key={item.id} c_id={item.id} group_name={item.groupName} message_count={item.count} participants={item.participant} count_by_day={item.count_by_day} x_axis={dates} />
          ))
      );
    }
  }
}

function App() {
  return (
    <div>
    <div className="container">
      <div className="row">
        <div className="col-12">
          <div className="hero mt-3 mb-3 text-center">
            <h1 className="display-4 font-weight-light">converscope</h1>
            <p className="lead font-italic">daylen's texts, 2010-2019</p>
            {/*<p className="lead font-italic">metadata reveals a lot</p>*/}
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-12">
        <div className="btn-toolbar mb-3">
          <div className="btn-group">
            <button type="button" className="btn btn-primary active">DMs</button>
            <button type="button" className="btn btn-primary">Groups</button>
          </div>
        </div>
        <ConversationList />
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;
