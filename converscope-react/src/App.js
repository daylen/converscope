import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import {Line} from 'react-chartjs-2';
import ToggleButtonGroup from 'react-bootstrap/ToggleButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Button from 'react-bootstrap/Button';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Dropdown from 'react-bootstrap/Dropdown';
import * as constants from './constants.js';
import DetailPage from './detail.js';
import { BrowserRouter as Router, Switch, Route, Link } from 'react-router-dom';

function ConversationPill(props) {
  return (
    <Link to={'/detail/' + props.c_id}>
    <div className="card mb-3">
      <div className="card-body">
        <h5 className=""><small className="text-danger">{props.c_id.substr(0,7)}</small> {props.group_name} <small className="text-muted">{props.message_count} messages</small></h5>
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
              pointRadius: .3,
              pointHitRadius: 10,
              data: props.count_by_day,
            }]
          }} height={"100%"} options={{
            animation: {duration: 0},
            hover: {animationDuration: 0},
            responsiveAnimationDuration: 0,
            elements: {line: {tension: 0}},
            maintainAspectRatio: false,
            legend: {
              display: false,
            },
            scales: {
              xAxes: [{
                type: 'time',
                time: {
                  unit: 'year',
                },
                minRotation: 0,
                maxRotation: 0,
                sampleSize: 1,
              }]
            }
          }} />
        </div>

      </div>
    </div>
    </Link>
  );
}

class CommandBar extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
      <ButtonToolbar>
      <ToggleButtonGroup type="radio" name="radio" value={this.props.groups} onChange={this.props.groups_callback} className="">
        <ToggleButton value={"0"} variant="warning">Direct Messages</ToggleButton>
        <ToggleButton value={"1"} variant="warning">Group Chats</ToggleButton>
      </ToggleButtonGroup>
      &nbsp;
      <DropdownButton id="sort-by-button" title={this.props.time_period} variant="warning">
        <Dropdown.Item eventKey="all_time" onSelect={this.props.time_period_callback}>all time</Dropdown.Item>
        <Dropdown.Item eventKey="last_year" onSelect={this.props.time_period_callback}>last year</Dropdown.Item>
        <Dropdown.Item eventKey="high_school" onSelect={this.props.time_period_callback}>high school</Dropdown.Item>
        <Dropdown.Item eventKey="college" onSelect={this.props.time_period_callback}>college</Dropdown.Item>
        <Dropdown.Item eventKey="post_college" onSelect={this.props.time_period_callback}>post college</Dropdown.Item>
      </DropdownButton>
      </ButtonToolbar>
      <hr />
      </div>
    );
  }
}

class ConversationList extends React.Component {
  render() {
    if (this.props.error) {
      return <div>Error: {this.props.error.message}</div>;
    } else {
      return (
        <div>
          <CommandBar groups={this.props.groups} time_period={['Sort by: count ', <b>{this.props.time_period.replace('_', ' ')}</b>]} groups_callback={this.props.setGroups} time_period_callback={this.props.setTimePeriod}/>
          {this.props.isLoaded ? 
          this.props.items.map(item => (
            <ConversationPill key={item.id} c_id={item.id} group_name={item.groupName} message_count={item.count} participants={item.participant} count_by_day={item.count_by_day} x_axis={this.props.dates} />
          )) : <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>}
        </div>
      );
    }
  }
}

class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      groups: "0",
      time_period: "all_time",
      error: null,
      isLoaded: false,
      items: [],
      dates: [],
      show_explainer: localStorage.getItem('show_explainer') === 'true'
    };
  }

  setGroups = (val) => {
    this.setState(prevState => {
      let newState = Object.assign({}, prevState);
      newState.groups = val;
      newState.isLoaded = false;
      return newState;
    }, () => {this.fetchData(true)});
  }

  setTimePeriod = (val) => {
    this.setState(prevState => {
      let newState = Object.assign({}, prevState);
      newState.time_period = val;
      newState.isLoaded = false;
      return newState;
    }, () => {this.fetchData(true)});
  }

  setShowExplainer = (val) => {
    this.setState(prevState => {
      localStorage.setItem('show_explainer', val);
      let newState = Object.assign({}, prevState);
      newState.show_explainer = val;
      return newState;
    })
  }

  fetchData = (forced) => {
    if (!forced && this.isLoaded) return;
    let url = constants.URL_PREFIX + "/api/conversations?groups=" + this.state.groups + '&time_period=' + this.state.time_period;
    fetch(url)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            groups: this.state.groups,
            time_period: this.state.time_period,
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
            time_period: this.state.time_period,
            isLoaded: true,
            error: error,
          });
        }
      )
  }

  componentDidMount() {
    this.fetchData(true);
  }

  render = () => {
    return (
      <Router>
      <div className="container">
        <div className="row">
          <div className="col-12">
            <div class="jumbotron mt-3">
              <h1 class="display-4"><Link to="/">converscope</Link></h1>
              <p class="lead">a <a href="https://daylen.com/">daylen yang</a> data experiment</p>
              {/*<p className="text-muted"><small>Inspired by <a href="http://hipsterdatascience.com/messages/" target="_blank">@cba's version</a></small></p>*/}
              <div className={this.state.show_explainer ? "" : "d-none"}>
              <hr />
              <p><b>What is this?</b> This is a visualization of every Facebook chat and iMessage I've ever sent/received in the last 10 years. <b>Each row is one person</b> (or group, if you flip the DMs/Groups toggle). The <b>x-axis is time</b>, and the <b>y-axis is the number of messages</b> sent that day. The rows are sorted by the all-time number of messages.</p>
              <p><b>Really, 10 years?</b> Mostly! The Facebook data starts at the end of 2010. The iMessages start mid-2014.</p>
              <p><b>Can I try my own chats?</b> Yes! The code is <a href="https://github.com/daylen/converscope">open source 🎉</a> so I encourage you to check it out.</p>
              </div>
              <p className="text-muted"><a href="#" onClick={() => this.setShowExplainer(!this.state.show_explainer)}><small>{this.state.show_explainer ? "Hide" : "Show"} explainer text</small></a></p>

            </div>
          </div>
        </div>
        <div className="row">
          <div className="col-12">
            <Switch>
              <Route exact path="/" render={() => (<ConversationList groups={this.state.groups} time_period={this.state.time_period} error={this.state.error} isLoaded={this.state.isLoaded} items={this.state.items} dates={this.state.dates} setGroups={this.setGroups} setTimePeriod={this.setTimePeriod} />)} />
              <Route path="/detail/:id" render={({match}) => (<DetailPage c_id={match.params.id} />)}/>
            </Switch>
          </div>
        </div>
      </div>
      </Router>

    );
  }
}

export default App;