import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Admin = () => {
    const [treeData, setTreeData] = useState(null);

    useEffect(() => {
        axios.get('/tree')
            .then(response => {
                setTreeData(response.data);
            })
            .catch(error => {
                console.error('Error fetching the tree data:', error);
            });
    }, []);

    const buildTreeHtml = (node) => {
        if (!node.children || node.children.length === 0) {
            return <li key={node.path}><a href={`/download/${node.path}`}>{node.name}</a></li>;
        }
        return (
            <li key={node.name}>
                {node.name}
                <ul>
                    {node.children.map(child => buildTreeHtml(child))}
                </ul>
            </li>
        );
    };

    const downloadAll = () => {
        window.location.href = '/download_all';
    };

    return (
        <div>
            <h1>Experiment Results Directory</h1>
            <button onClick={downloadAll}>Download All Experiments</button>
            {treeData ? (
                <ul>
                    {buildTreeHtml(treeData)}
                </ul>
            ) : (
                <p>Loading tree data...</p>
            )}
        </div>
    );
};

export default Admin;
