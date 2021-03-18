// class MyStartTimeExtension implements iApplicationObjectExtension {
//     public function OnDBInsert($oObject, $oChange = null){
//         if(!is_null($oChange) && DBObject::GetClassName($oObject) == 'OnCall'){
//             $oObject->Set('end_datetime', date('Y-m-d 23:59:59', strtotime($oObject->Get('end_day'))));
//         }
//     }
// }

// class MyStartTimeUIExtension implements iApplicationUIExtension {
//     public function OnDisplayProperties(DBObject $oObject, Webpage $oPage, boolean $bEditMode){
//         if($bEditMode){
//             
//         }else{
//             
//         }
//     }
// }

// public function DoCheckToWrite(){
//     parent::DoCheckToWrite();
// 
//     if(MetaModel::IsValidAttCode(get_class($this), 'day')
//         && MetaModel::IsValidAttCode(get_class($this), 'repeat_until_end_of')
//         && (AttributeDateTime::GetAsUnixSeconds($this->Get('day'))
//             > AttributeDateTime::GetAsUnixSeconds($this->Get('repeat_until_end_of'))
//         )
//     ){
//         $this->m_aCheckIssues[] = Dict::Format('Class:Error:RepeatUntilEndOfMustBeGreaterThanDay');
//     }
// }
