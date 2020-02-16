import React from 'react';
import {Line} from 'react-chartjs-2';

function MessageCountHistogram(props) {
	return (<div className="chart">
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
              data: props.counts,
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
                  unit: (props.by_week || props.x_axis.length > 365) ? 'year' : 'month',
                },
                minRotation: 0,
                maxRotation: 0,
                sampleSize: 1,
              }],
              yAxes: [{
                ticks: {display: !props.by_week }
              }]
            },
            tooltips: { enabled: !props.by_week }
          }} />
        </div>);
}

export default MessageCountHistogram;
