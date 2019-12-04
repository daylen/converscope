import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import {Line} from 'react-chartjs-2';
import ToggleButtonGroup from 'react-bootstrap/ToggleButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Button from 'react-bootstrap/Button';

function ConversationPill(props) {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="">{props.group_name} <small className="text-muted">{props.message_count} messages</small></h5>
        <div className="text-muted small">
          <ul className="participants">{props.participants.length > 2 ? props.participants.map((name) => <li key={props.c_id + name}>{name}</li>) : ""}</ul>
        </div>
        <div className="chart">
          <Line data={{
            labels: props.x_axis,
            datasets: [{
              label: 'num messages',
              fill: false,
              lineTension: 0.1,
              borderColor: 'rgba(75,192,192,0.5)',
              borderWidth: 2,
              pointBorderColor: 'rgba(75,192,192,1)',
              pointHoverRadius: 5,
              pointHoverBackgroundColor: 'rgba(75,192,192,1)',
              pointHoverBorderWidth: 2,
              pointRadius: 1,
              pointHitRadius: 10,
              data: props.count_by_day
            }]
          }} height={"100%"} options={{
            maintainAspectRatio: false,
            legend: {
              display: false,
            },
            scales: {
              xAxes: [{
                type: 'time',
                time: {
                  unit: 'year',
                }
              }]
            }
          }} />
        </div>

      </div>
    </div>
  );
}

class CommandBar extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <ToggleButtonGroup type="radio" name="radio" value={this.props.groups} onChange={this.props.callback} className="mb-3">
        <ToggleButton value={"0"} variant="info">DMs</ToggleButton>
        <ToggleButton value={"1"} variant="info">Groups</ToggleButton>
      </ToggleButtonGroup>
    );
  }
}

class ConversationList extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (this.props.error) {
      return <div>Error: {this.props.error.message}</div>;
    } else if (!this.props.isLoaded) {
      return (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
          this.props.items.map(item => (
            <ConversationPill key={item.id} c_id={item.id} group_name={item.groupName} message_count={item.count} participants={item.participant} count_by_day={item.count_by_day} x_axis={this.props.dates} />
          ))
      );
    }
  }
}

class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      groups: "0",
      error: null,
      isLoaded: false,
      items: [],
      dates: [],
    };
  }

  setGroups = (val) => {
    this.setState({
      groups: val,
      error: null,
      isLoaded: false,
      items: [],
      dates: [],
    }, this.fetchData);
    
  }

  fetchData() {
    fetch("http://dawn.local:5000/api/conversations?groups=" + this.state.groups)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            groups: this.state.groups,
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
            groups: this.state.groups,
            isLoaded: true,
            error: error,
          });
        }
      )
  }

  componentDidMount() {
    this.fetchData();
  }

  render = () => {
    return (
      <div>
      <div className="container">
        <div className="row">
          <div className="col-12">
            <div className="hero mt-3 mb-3 text-center">
              <h1 className="display-4 font-weight-light">converscope</h1>
              <p className="lead font-italic">9 years of daylen's texts</p>
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col-12">
            <CommandBar groups={this.state.groups} callback={this.setGroups}/>
            <ConversationList error={this.state.error} isLoaded={this.state.isLoaded} items={this.state.items} dates={this.state.dates} />
          </div>
        </div>
      </div>
      </div>
    );
  }
}

export default App;
