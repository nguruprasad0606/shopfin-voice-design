import EmptyState from '../components/common/EmptyState'
export default function Placeholder({name}:{name:string}){return <div className="card"><EmptyState title={`${name} is coming in the next phase`} hint="This page isn't built yet."/></div>}
